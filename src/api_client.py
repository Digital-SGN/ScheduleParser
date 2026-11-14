import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from tqdm import tqdm
from exceptions import APIError, FilialNotFoundError

BASE_URL = 'https://lks.bmstu.ru/lks-back/api/v1'
DEFAULT_TIMEOUT = 30
DEFAULT_WORKERS = 16

logger = logging.getLogger(__name__)

_thread_local = threading.local()


def _get_session() -> requests.Session:
    """Возвращает HTTP-сессию, привязанную к текущему потоку."""
    session = getattr(_thread_local, 'session', None)
    if session is None:
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'schedule-parser/1.3',
            'Accept': 'application/json',
        })
        _thread_local.session = session

    return session


def get_group_schedule(
        group_id: str,
        session: requests.Session | None = None,
        *,
        timeout: int = DEFAULT_TIMEOUT
) -> dict:
    """
    Загружает расписание одной учебной группы.

    Args:
        group_id: UUID учебной группы.
        session: HTTP-сессия; если не передана — берётся thread-local.
        timeout: Таймаут запроса в секундах.

    Returns:
        Словарь ``{название_группы: список_занятий}``. Пустой словарь,
        если у группы нет расписания.

    Raises:
        APIError: Сервер вернул статус, отличный от 200 или 204.
    """
    url = f'{BASE_URL}/schedules/groups/{group_id}/public'
    http = session or _get_session()
    response = http.get(url, timeout=timeout)

    if response.status_code == 204:
        return {}
    if response.status_code != 200:
        raise APIError(
            f'Не удалось получить расписание группы {group_id}: '
            f'HTTP {response.status_code}'
        )

    data = response.json()['data']
    return {data['title']: data['schedule']}


def get_groups_schedule(
    group_ids: list[str],
    workers: int = DEFAULT_WORKERS,
    *,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict:
    """
    Параллельно загружает расписания всех указанных групп.

    Args:
        group_ids: Список UUID учебных групп.
        workers: Количество потоков.
        timeout: Таймаут одного запроса в секундах.

    Returns:
        Объединённый словарь {название_группы: список_занятий}.
    """
    group_schedules: dict = {}
    total = len(group_ids)
    empty = 0
    failed = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(get_group_schedule, gid, timeout=timeout): gid
            for gid in group_ids
        }
        with tqdm(total=total, desc='Получение расписаний', unit='гр') as bar:
            for future in as_completed(futures):
                gid = futures[future]
                try:
                    schedule = future.result()
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    logger.warning('Ошибка группы %s: %s', gid, exc)
                else:
                    if schedule:
                        group_schedules.update(schedule)
                    else:
                        empty += 1
                bar.update(1)
                bar.set_postfix(empty=empty, failed=failed, refresh=False)

    if empty:
        logger.info('Групп без расписания: %d', empty)
    if failed:
        logger.warning('Не удалось получить: %d из %d', failed, total)

    return group_schedules


def get_group_uuids(
        filial_uuid: str,
        *,
        timeout: int = DEFAULT_TIMEOUT
) -> list[str]:
    """
    Возвращает UUID всех учебных групп указанного филиала.

    Args:
        filial_uuid: UUID филиала.
        timeout: Таймаут запроса в секундах.

    Returns:
        Список UUID всех найденных групп.

    Raises:
        APIError: Не удалось загрузить структуру.
        FilialNotFoundError: Филиал с указанным UUID отсутствует.
    """
    url = f'{BASE_URL}/structure'
    response = requests.get(url, timeout=timeout)

    if response.status_code != 200:
        raise APIError(
            f'Не удалось получить структуру: HTTP {response.status_code}'
        )

    data = response.json()

    for filial in data['data']['children']:
        if filial['uuid'] != filial_uuid:
            continue

        group_ids: list[str] = []
        for faculty in filial['children']:
            for department in faculty['children']:
                for course in department['children']:
                    for group in course['children']:
                        group_ids.append(group['uuid'])
        return group_ids

    raise FilialNotFoundError(f'Филиал {filial_uuid} не найден')

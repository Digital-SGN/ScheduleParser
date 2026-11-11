import requests
from exceptions import ScheduleNotFoundError, GroupNotFoundError
from tqdm import tqdm


def get_group_schedule(group_id: str) -> dict:
    """
    Получает расписание указанной учебной группы.

    Args:
        group_id: UUID учебной группы.

    Returns:
        Словарь, в котором ключом является название группы,
        а значением — её расписание.

    Raises:
        ScheduleNotFoundError: Если расписание не найдено.
    """
    url: str = (
        f'https://lks.bmstu.ru/lks-back/api/v1/schedules/groups/{group_id}/public'
    )

    response: requests.Response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()["data"]

        group_schedule: dict = {
            data["title"]: data["schedule"]
        }

        return group_schedule

    raise ScheduleNotFoundError("Расписание не найдено")


def get_groups_schedule(group_ids: list[str]) -> dict:
    """
    Получает расписания нескольких учебных групп.

    Последовательно отправляет запросы для каждой группы и объединяет
    полученные расписания в один словарь. Отображает ход выполнения
    операции с помощью индикатора прогресса.

    Args:
        group_ids: Список UUID учебных групп.

    Returns:
        Словарь, содержащий названия групп и соответствующие им расписания.

    Raises:
        ScheduleNotFoundError: Если расписание хотя бы одной группы не найдено.
    """
    group_schedules: dict = {}

    for group_id in tqdm(
        group_ids,
        desc="Получение расписаний",
        unit="группа"
    ):
        schedule: dict = get_group_schedule(group_id)

        group_schedules.update(schedule)

    return group_schedules


def get_group_uuids(filial_uuid: str) -> list[str]:
    """
    Получает UUID всех учебных групп указанного филиала.

    Загружает структуру университета из API и последовательно обходит
    вложенную иерархию: филиалы, факультеты, кафедры, курсы и группы.
    Отображает ход поиска филиала и обработки факультетов.

    Args:
        filial_uuid: UUID филиала, для которого необходимо найти группы.

    Returns:
        Список UUID всех учебных групп найденного филиала.

    Raises:
        GroupNotFoundError: Если филиал с указанным UUID не найден.
        requests.exceptions.Timeout: Если превышено время ожидания ответа.
        requests.exceptions.ConnectionError: Если не удалось установить соединение.
        requests.exceptions.RequestException: Если произошла другая ошибка запроса.
    """
    url: str = 'https://lks.bmstu.ru/lks-back/api/v1/structure'

    response: requests.Response = requests.get(url, timeout=30)

    if response.status_code == 200:
        data = response.json()
        group_ids: list[str] = []

        for filial in tqdm(
            data["data"]["children"],
            desc="Поиск филиала",
            unit="филиал"
        ):
            if filial["uuid"] == filial_uuid:

                for faculty in tqdm(
                    filial["children"],
                    desc="Обработка факультетов",
                    unit="факультет",
                    leave=False
                ):
                    for department in faculty["children"]:

                        for course in department["children"]:

                            for group in course["children"]:
                                group_ids.append(group["uuid"])

                return group_ids

    raise GroupNotFoundError(f'Группа {filial_uuid} не найдена')
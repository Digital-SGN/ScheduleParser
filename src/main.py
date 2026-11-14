import datetime
import logging

from tqdm import tqdm

import settings
from api_client import get_group_uuids, get_groups_schedule
from exceptions import APIError, FilialNotFoundError
from file_creator import save_schedule
from parser import parse_schedule


class _TqdmHandler(logging.Handler):
    """Пишет логи через ``tqdm.write``, не ломая прогресс-бар."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            tqdm.write(self.format(record))
        except Exception:
            self.handleError(record)


def _setup_logging(verbose: bool) -> None:
    """
    Настраивает корневой логгер на вывод через ``_TqdmHandler``.

    Args:
        verbose: ``True`` — уровень DEBUG, иначе WARNING.
    """
    handler = _TqdmHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.WARNING,
        handlers=[handler],
        force=True,
    )


def _say(message: str) -> None:
    """Печатает строку через ``tqdm.write``, не ломая прогресс-бар."""
    tqdm.write(message)


def run() -> None:
    """
    Точка входа в приложение.

    Raises:
        SystemExit: Код 1 при любой фатальной ошибке (структура, сеть, запись файла).
    """
    _setup_logging(settings.VERBOSE)

    _say('Парсер расписания МГТУ им. Баумана')
    _say(
        f'Филиал: {settings.FILIAL}  |  '
        f'Старт: {settings.START_DATE}  |  '
        f'недель: {settings.WEEKS}  |  '
        f'потоков: {settings.WORKERS}'
    )

    start_date = datetime.date.fromisoformat(settings.START_DATE)

    try:
        group_ids = get_group_uuids(settings.FILIAL, timeout=settings.TIMEOUT)
    except (FilialNotFoundError, APIError) as exc:
        _say(f'ERROR: {exc}')
        raise SystemExit(1)
    _say(f'OK: найдено групп: {len(group_ids)}')

    if not group_ids:
        _say('ERROR: в филиале нет групп')
        raise SystemExit(1)

    schedules = get_groups_schedule(
        group_ids,
        workers=settings.WORKERS,
        timeout=settings.TIMEOUT,
    )
    _say(f'OK: получено расписаний: {len(schedules)}')

    if not schedules:
        _say('ERROR: не получено ни одного расписания')
        raise SystemExit(1)

    lessons = parse_schedule(schedules, settings.WEEKS, start_date)
    _say(f'OK: занятий: {len(lessons)}')

    try:
        save_schedule(lessons, settings.OUTPUT)
    except OSError as exc:
        _say(f'ERROR: не удалось сохранить файл: {exc}')
        raise SystemExit(1)

    _say(f'DONE: сохранено в {settings.OUTPUT}')


if __name__ == '__main__':
    run()

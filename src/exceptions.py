class APIError(Exception):
    """Базовое исключение для ошибок API."""
    pass


class GroupNotFoundError(APIError):
    """Группа не найдена."""
    pass


class ScheduleNotFoundError(APIError):
    """Расписание не найдено."""
    pass
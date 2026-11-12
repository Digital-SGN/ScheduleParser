class APIError(Exception):
    """Базовое исключение для ошибок API."""
    pass


class FilialNotFoundError(APIError):
    """Филиал не найден."""
    pass
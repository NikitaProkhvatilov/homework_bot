class WrongStatus(Exception):
    """Исключение, если был получен неожиданный статус ответа."""


class CurrentDateNotFound(Exception):
    """Исключение, если не был найден ключ current_date."""

class CurrentDateWrongFormat(Exception):
    """Исключение, если формат ключа current_date не соответствует ожидаемому."""
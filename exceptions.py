class WrongStatus(Exception):
    """Исключение.
    Был получен неожиданный статус ответа.
    """


class CurrentDateNotFound(Exception):
    """Исключение.
    Не был найден ключ current_date.
    """


class CurrentDateWrongFormat(Exception):
    """Исключение.
    Формат значения ключа current_date
    не соответствует ожидаемому.
    """

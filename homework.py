import json
import logging
import os
from pathlib import Path
import sys
import time

from dotenv import load_dotenv
import requests
from telebot import TeleBot, apihelper

from exceptions import WrongStatus, CurrentDateNotFound, CurrentDateWrongFormat

load_dotenv()

PRACTICUM_TOKEN = os.getenv('HOMEWORK_TOKEN')
TELEGRAM_TOKEN = os.getenv('BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
FORMAT = (
    '%(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d  %(message)s')

BASE_DIR = os.path.dirname(Path(__file__))

logger = logging.getLogger(__name__)


def check_tokens():
    """Проверка наличия доступности переменных окружения."""
    tokens = {
        'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
        'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID}
    for token in tokens:
        if not tokens[token]:
            logger.critical(
                f'Не найдена переменная окружения: {token}')
    if not all(tokens.values()):
        sys.exit(1)


def send_message(bot, message):
    """Отправка сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except (apihelper.ApiException, requests.RequestException) as error:
        logger.error(f'Не удалось отправить сообщение: {error}')
    else:
        logger.debug('Сообщение отправлено.')


def get_api_answer(timestamp):
    """Отправка запроса и получение ответа."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
    except requests.RequestException as error:
        raise ConnectionError(
            f'Не удалось получить ответ сервера: {error}')
    if response.status_code != 200:
        raise WrongStatus(
            f'Неожиданный стаутс ответа: {response.status_code}')
    try:
        return response.json()
    except json.JSONDecodeError as error:
        raise json.JSONDecodeError(f'Ошибка формата ответа: {error}')


def check_response(response):
    """Получение последней сданной работы."""
    if not isinstance(response, dict):
        raise TypeError('Неверный формат данных, ожидается словарь.')
    if response.get('current_date') is None:
        raise CurrentDateNotFound('Ключ current_date отсутствует.')
    if not isinstance(response.get('current_date'), int):
        raise CurrentDateWrongFormat('Значения ключа current_date'
                                     'не соответствует ожидаемому'
                                     'типу данных.')
    if response.get('homeworks') is None:
        raise KeyError('Отсутствует ключ homeworks')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Неверный формат данных, ожидается список.')
    return homeworks


def parse_status(homeworks):
    """Получение статуса работы и формирование сообщения."""
    homework_name = homeworks.get('homework_name')
    if not homework_name:
        raise KeyError('Ошибка получения имени.')
    status = homeworks.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError('Ошибка получения статуса.')
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    last_status = None
    timestamp = 0
    check_tokens()
    while True:
        try:
            answer = get_api_answer({'from_date': timestamp})
            timestamp = answer.get('current_date')
            homeworks = check_response(answer)
            if len(homeworks) != 0:
                message = parse_status(homeworks[0])
            else:
                message = 'Список домашних работ пуст.'
                logger.debug('Домашние работы не найдены.')
        except (CurrentDateNotFound, CurrentDateWrongFormat) as error:
            logger.error(error)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(error)
        finally:
            if message != last_status:
                last_status = message
                send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        format=FORMAT,
        level=logging.DEBUG,
        filename=os.path.join(BASE_DIR, 'main.log'),
        filemode='w'
    )
    main()

import logging
import os
import sys
import time

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler
import requests
from telebot import TeleBot

from exceptions import HomeworkNotFound

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='main.log',
    filemode='w'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('main.log', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


def check_tokens():
    """Проверка наличия доступности переменных окружения."""
    if not PRACTICUM_TOKEN:
        logging.critical('Не найден токен практикума!')
    if not TELEGRAM_TOKEN:
        logging.critical('Не найден токен бота!')
    if not TELEGRAM_CHAT_ID:
        logging.critical('Не найден ID чата!')
    if all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)):
        logging.info('Все токены в наличии')
        return None
    sys.exit()


def send_message(bot, message):
    """Отправка сообщения."""
    chat_id = TELEGRAM_CHAT_ID
    try:
        bot.send_message(chat_id, message)
        logging.debug('Сообщение отправлено.')
    except Exception as error:
        logging.error(error, exc_info=True)
        logging.debug('Сообщение не отправлено.')


def get_api_answer(timestamp):
    """Отправка запроса и получение ответа."""
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=timestamp)
        if response.status_code != 200:
            raise Exception('Ответ не получен')
        response = response.json()
        return response
    except response.status_code != 200:
        logging.error(exc_info=True)


def check_response(response):
    """Получение последней сданной работы."""
    if not isinstance(response, dict):
        raise TypeError('Неверный формат данных, ожидается словарь.')
    if response.get('homeworks') is None:
        raise KeyError('Отсутствует ключ homeworks')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Неверный формат данных, ожидается список.')
    if len(homeworks) == 0:
        raise HomeworkNotFound('Домашняя работа не найдена')
    return homeworks[0]


def parse_status(homework):
    """Получение статуса работы и формирование сообщения."""
    homework_name = homework.get('homework_name')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise KeyError('Ошибка получения статуса.')
    verdict = HOMEWORK_VERDICTS[status]
    if not homework_name:
        raise KeyError('Ошибка получения имени.')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    payload = {'from_date': timestamp}
    last_status = None
    while True:
        try:
            check_tokens()
            answer = get_api_answer(payload)
            homework = check_response(answer)
            status = parse_status(homework)
            new_status = status
            if new_status != last_status:
                last_status = new_status
                send_message(bot, status)
                time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(error, exc_info=True)
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()

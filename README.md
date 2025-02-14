# Homework_Bot
## Описание проекта
Telegram-бот, который регулярно проверяет статус отправленной домашней работы, если статус изменился, то бот уведомляет об этом.
## Локальный запуск проекта
#### Клонируйте репозиторий
```
git@github.com:NikitaProkhvatilov/homework_bot.git
```
#### Перейдите в директорию Movie_bot
```
cd homework_bot
```
#### Cоздайте и активируйте виртуальное окружение:
```
python -m venv venv
```
```
source venv/bin/activate
```
#### Установите зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

В той же директории создайте .env файл и наполните его своими данными:
```
HOMEWORK_TOKEN          - токен API Яндекс Практикум
BOT_TOKEN               - токен вашего бота
ID                      - ваш ID в Telegram
```
### Начало работы
Запустите файл __homework.py__, после чего запустите чат с ботом в Telegram.

### Технологии
_Используемые технологии_: __Python 3__, __pyTelegramBotAPI__

### Автор
_Никита Прохватилов_

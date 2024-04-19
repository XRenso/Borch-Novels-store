from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv, find_dotenv
import os
import logging
from database import Mongo as mg






if not find_dotenv():
    exit("Переменные окружения не загружены т.к отсутствует файл .env")
else:
    load_dotenv()

db = mg()
db.__init__()
WEBHOOK_PATH = f'/bot/{os.getenv("TOKEN")}'
WEBHOOK_URL = f'{os.getenv("NGROK_URL")}{WEBHOOK_PATH}'
WENHOOK_HOST = f'{os.getenv("HOST")}'

bot = Bot(token=os.getenv('TOKEN'), parse_mode='HTML')
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("donate", "Поддержать проект"),
        BotCommand("info","Информация про наш магазин"),
        BotCommand("reset_game", "Сбросить прогресс в игре"),
        BotCommand("cancel", "Отменить ввод")
    ])
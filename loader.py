from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage # просто, хранящее информацию в ОП
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
storage = MemoryStorage()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        BotCommand("start", "Запустить бота"),
        BotCommand("donate", "Поддержать проект"),
        BotCommand("reset_game", "Сбросить прогресс в игре")
    ])
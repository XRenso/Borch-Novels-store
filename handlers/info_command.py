import phrase as phr
from loader import dp
from aiogram import types
@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    await message.answer(phr.info_text)
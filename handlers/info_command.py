import phrase as phr
from loader import dp
from aiogram import types
from aiogram.filters.command import Command
@dp.message(Command('info'))
async def start(message: types.Message):
    await message.answer(phr.info_text)
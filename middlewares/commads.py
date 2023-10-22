from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram.types import BotCommand
from aiogram import types
from loader import db,dp
class Commands(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data:dict):
        user_id = update.message.from_user.id
        user = db.return_user_info(user_id)
        if not user['is_admin']:
            await dp.bot.set_my_commands([
                BotCommand("start", "Запустить бота"),
                BotCommand("donate", "Поддержать проект"),
                BotCommand("info", "Информация про наш магазин"),
                BotCommand("reset_game", "Сбросить прогресс в игре"),
                BotCommand("cancel", "Отменить ввод")
            ])
        else:
            await dp.bot.set_my_commands([
                BotCommand("start", "Запустить бота"),
                BotCommand("donate", "Поддержать проект"),
                BotCommand("info", "Информация про наш магазин"),
                BotCommand("reset_game", "Сбросить прогресс в игре"),
                BotCommand("cancel", "Отменить ввод"),
                BotCommand('set_tech_mode','Переключить тех. режим')
            ])
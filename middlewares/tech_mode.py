from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram import types
from loader import db
class Server_status(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data:dict):
        if db.is_bot_in_tech_mode():
            user_id = update.message.from_user.id
            user = db.return_user_info(user_id)
            if not user['is_admin']:
                await update.message.answer('🤖 Бот находится на техобслуживание. Подождите немного.\n'
                                            '📰 Следите за новостями в нашем тг канале - @BorchStore')
                raise CancelHandler()
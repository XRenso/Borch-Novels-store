from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from aiogram import types
from loader import db
class Server_status(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data:dict):
        if db.is_bot_in_tech_mode():
            try:
                user_id = message.from_user.id
                user = db.return_user_info(user_id)
                try:
                    if not user['is_admin']:
                        await message.answer('🤖 Бот находится на техобслуживание. Подождите немного.\n'
                                                    '📰 Следите за новостями в нашем тг канале - @BorchStore')
                        raise CancelHandler()
                except TypeError:
                    await message.answer('🤖 Бот находится на техобслуживание. Подождите немного.\n'
                                         '📰 Следите за новостями в нашем тг канале - @BorchStore')
                    raise CancelHandler()
            except AttributeError:
                pass

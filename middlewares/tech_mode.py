from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any
from loader import db,dp
class Server_status(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        try:
            user_id = event.from_user.id
            user = db.return_user_info(user_id)
        except AttributeError:
            user_id = None
            user = None
        if db.is_bot_in_tech_mode():

                if user:
                    if not user['is_admin']:
                        await event.answer('🤖 Бот находится на техобслуживание. Подождите немного.\n'
                                                    '📰 Следите за новостями в нашем тг канале - @BorchStore')
                    else:
                        return await handler(event, data)


        else:
            return await handler(event, data)



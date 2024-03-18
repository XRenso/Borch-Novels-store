from aiogram import BaseMiddleware
from aiogram.types import BotCommand
from aiogram.types import Message
from typing import Callable, Awaitable, Dict, Any
from loader import db,dp, bot
class Commands(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        user = db.return_user_info(user_id)
        try:
            if not user['is_admin']:
                await bot.set_my_commands([
                    BotCommand(command="start", description="Запустить бота"),
                    BotCommand(command="donate", description="Поддержать проект"),
                    BotCommand(command="info", description="Информация про наш магазин"),
                    BotCommand(command="reset_game", description="Сбросить прогресс в игре"),
                    BotCommand(command="cancel", description="Отменить ввод")
                ])
            else:
                await bot.set_my_commands([
                    BotCommand(command="start", description="Запустить бота"),
                    BotCommand(command="donate", description="Поддержать проект"),
                    BotCommand(command="info", description="Информация про наш магазин"),
                    BotCommand(command="reset_game", description="Сбросить прогресс в игре"),
                    BotCommand(command="cancel", description="Отменить ввод"),
                    BotCommand(command='set_tech_mode',description='Переключить тех. режим'),
                    BotCommand(command='send_everyone',description='Отправить всем сообщение')
                ])
        except TypeError:
            await bot.set_my_commands([
                BotCommand(command="start", description="Запустить бота"),
                BotCommand(command="donate", description="Поддержать проект"),
                BotCommand(command="info", description="Информация про наш магазин"),
                BotCommand(command="reset_game", description="Сбросить прогресс в игре"),
                BotCommand(command="cancel", description="Отменить ввод")
            ])
        return await handler(event,data)
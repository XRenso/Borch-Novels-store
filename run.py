from loader import dp,bot, set_default_commands, db
import loader
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares import tech_mode, commads
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram import types

from handlers import buy_game, donate, frame_mechanics, game_card, game_rate, game_reset,\
    inline_mode, payment, profile, send_file_id,  store_catalog, store_actions, user_groups,start, info_command,\
    set_tech_mode,send_everyone,\
    text_commands, admin_info_frame


async def clear_month_sales():
    db.clear_month_sale()

async def on_startup():
    await bot.delete_webhook(drop_pending_updates=True)
    webhook_info = await bot.get_webhook_info()
    if webhook_info.url != loader.WEBHOOK_URL:
        await bot.set_webhook(
            url=loader.WEBHOOK_URL
        )
def main():

    dp.startup.register(on_startup)
    app = web.Application()
    webhook_request_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot = bot
    )
    webhook_request_handler.register(app,path=loader.WEBHOOK_PATH)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_month_sales, 'cron', month='1-12')
    scheduler.start()
    dp.message.outer_middleware.register(tech_mode.Server_status())
    dp.message.middleware.register(commads.Commands())
    setup_application(app,dp,bot=bot)
    web.run_app(app=app,host=loader.WENHOOK_HOST,port=80)
    # await bot.delete_webhook(drop_pending_updates=True)
    # await dp.start_polling(bot)
if __name__ == '__main__':
    main()
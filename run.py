from loader import dp,bot, set_default_commands, db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares import tech_mode, commads
import asyncio
from handlers import buy_game, donate, frame_mechanics, game_card, game_rate, game_reset,\
    inline_mode, payment, profile, send_file_id,  store_catalog, store_actions, user_groups,start, info_command,\
    set_tech_mode,send_everyone,\
    text_commands, admin_info_frame


async def clear_month_sales():
    db.clear_month_sale()


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_month_sales, 'cron', month='1-12')
    scheduler.start()
    dp.message.outer_middleware.register(tech_mode.Server_status())
    dp.message.middleware.register(commads.Commands())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
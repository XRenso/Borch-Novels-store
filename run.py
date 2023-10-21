from loader import dp,bot, set_default_commands, db
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from middlewares import tech_mode, commads
from handlers import buy_game, donate, frame_mechanics, game_card, game_rate, game_reset,\
    inline_mode, payment, profile, send_file_id,  store_catalog, store_actions, user_groups,start, info_command,\
    set_tech_mode,\
    text_commands, admin_info_frame


async def clear_month_sales():
    db.clear_month_sale()

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_month_sales, 'cron', month='1-12')
    scheduler.start()
    dp.middleware.setup(tech_mode.Server_status())
    dp.middleware.setup(commads.Commands())
    executor.start_polling(dp,skip_updates=True)
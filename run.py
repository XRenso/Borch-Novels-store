from loader import dp,bot, set_default_commands, db
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers import text_commands, buy_game, donate, frame_mechanics, game_card, game_rate, game_reset,\
    inline_mode, payment, profile, send_file_id, start, store_catalog, store_actions, user_groups


async def clear_month_sales():
    db.clear_month_sale()

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_month_sales, 'cron', month='1-12')
    scheduler.start()
    executor.start_polling(dp,skip_updates=True,on_startup=set_default_commands)
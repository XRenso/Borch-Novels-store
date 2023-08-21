from loader import dp,bot, set_default_commands, db
from aiogram.utils import executor
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers import *


async def clear_month_sales():
    db.clear_month_sale()

if __name__ == '__main__':
    scheduler = AsyncIOScheduler()
    scheduler.add_job(clear_month_sales, 'cron', month='1-12')
    scheduler.start()
    executor.start_polling(dp,skip_updates=True,on_startup=set_default_commands)
import aiogram
from loader import db,dp,bot
import keyboards as kb
from aiogram import types
import phrase as phr
import hashlib
from aiogram.types import InlineKeyboardMarkup , InlineQueryResultCachedPhoto
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardButton, KeyboardButton)


@dp.inline_query()
async def send_game_info_inline(inline_query:types.InlineQuery):
    text = inline_query.query or ''
    games = db.search_game_by_name(text)
    results = []
    if games != 0:
        results = []
        for i in games:
            markup = InlineKeyboardBuilder().add(InlineKeyboardButton(text='Перейти к боту', url=f'https://t.me/BorchStoreBot?start={i["game_code"]}'))
            caption = phr.get_product_info(i)
            item = InlineQueryResultCachedPhoto(
                id = hashlib.md5(i['game_cover'].split('\n')[0].encode()).hexdigest(),
                title=i['game_name'],
                description=i['game_name'],
                photo_file_id=i['game_cover'].split('\n')[0],
                caption=caption,
                reply_markup=markup.as_markup() # {"id": "2074719242475204628", "from": {"id": 483058216, "is_bot": false, "first_name": "Товарищ", "last_name": "Рабочий", "username": "XRenso", "language_code": "ru"}, "inline_message_id": "AgAAAC93AgAo4socCpCtTODotO8", "chat_instance": "2634033057511433901", "data": "game:guide_store"}
            )
            results.append(item)
    await bot.answer_inline_query(inline_query.id,results,cache_time=1)

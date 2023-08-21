import aiogram
from loader import db,dp,bot
import keyboards as kb
from aiogram import types
import phrase as phr
import hashlib
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultCachedPhoto

@dp.callback_query_handler(kb.inline_show_game_info.filter())
async def send_game_info_by_inline_mode(call:types.CallbackQuery, callback_data: dict):
    game = db.return_game_info(callback_data['game_code'])
    media = types.MediaGroup()
    if db.return_user_info(call['from']['id']) != 0:
        markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call['from']['id'],game['game_code']), game['price'], user_id=call['from']['id'])
        for index, file_id in enumerate(game['game_cover'].split('\n')):
            match index:
                case _:
                    match file_id.lower()[0]:
                        case 'b':
                            media.attach_video(video=file_id)
                        case 'a':
                            media.attach_photo(photo=file_id)

        game_info_text = phr.get_product_info(game)
        try:
            await call.bot.send_media_group(chat_id=call['from']['id'],media=media)
            await call.bot.send_message(chat_id=call['from']['id'],text=game_info_text, reply_markup=markup)
        except aiogram.utils.exceptions.BotBlocked:
            await bot.answer_callback_query(call.id, 'Разблокируйте бота', True)
    else:

        await bot.answer_callback_query(call.id, 'Сначала пройдите регистрацию', True)
    await bot.answer_callback_query(call.id)

@dp.inline_handler()
async def send_game_info_inline(inline_query:types.InlineQuery):
    text = inline_query.query or ''
    games  = db.search_game_by_name(text)
    results = []
    if games != 0:
        results = []
        for i in games:
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton('Перейти к боту', url='https://t.me/BorchStoreBot?start=inline'))
            caption = phr.get_product_info(i)
            item = InlineQueryResultCachedPhoto(
                id = hashlib.md5(i['game_cover'].split('\n')[0].encode()).hexdigest(),
                title=i['game_name'],
                description=i['game_name'],
                photo_file_id=i['game_cover'].split('\n')[0],
                caption=caption,
                reply_markup=markup.add(InlineKeyboardButton('Получить информацию об игре', callback_data=kb.inline_show_game_info.new(i['game_code']))) # {"id": "2074719242475204628", "from": {"id": 483058216, "is_bot": false, "first_name": "Товарищ", "last_name": "Рабочий", "username": "XRenso", "language_code": "ru"}, "inline_message_id": "AgAAAC93AgAo4socCpCtTODotO8", "chat_instance": "2634033057511433901", "data": "game:guide_store"}
            )
            results.append(item)
    await bot.answer_inline_query(inline_query.id,results,cache_time=1)

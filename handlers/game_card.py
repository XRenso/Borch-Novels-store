import aiogram.utils.exceptions

from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import phrase as phr

@dp.callback_query_handler(kb.get_game_info.filter())
async def show_game_info(call:types.CallbackQuery, callback_data:dict):
    game = db.return_game_info(callback_data['game_code'])
    markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call.message.chat.id, game['game_code']),
                         game['price'], user_id=call.message.chat.id)

    game_info_text = phr.get_product_info(game)
    try:
        await call.message.edit_text(game_info_text, reply_markup=markup)
    except aiogram.utils.exceptions.BadRequest:
        try:
            await call.message.delete()
        except:
            await call.message.edit_caption('Сессия закрытка', reply_markup=None)
        await call.message.answer(game_info_text,reply_markup=markup)

@dp.callback_query_handler(kb.game_statistic.filter())
async def show_game_statistic(call:types.CallbackQuery, callback_data:dict):
    statistic_text = db.return_game_satistic(callback_data['game_code'])
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(callback_data['game_code'])))
    try:
        await call.message.edit_text(statistic_text,reply_markup=markup)
    except:
        await call.message.delete()
        await call.message.answer(statistic_text, reply_markup=markup)


@dp.callback_query_handler(kb.delete_game_from_library.filter())
async def delete_game_from_library(call:types.CallbackQuery, callback_data:dict):
    game_code = callback_data['game_code']
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(callback_data['game_code'])))
    db.delete_game_from_user_library(call.message.chat.id, game_code)
    try:
        await call.message.edit_text(phr.success_game_delete,reply_markup=markup)
    except:
        await call.message.delete()
        await call.message.answer(phr.success_game_delete, reply_markup=markup)

@dp.callback_query_handler(kb.show_more_info_game.filter())
async def show_game_info(call:types.CallbackQuery, callback_data: dict):
    game = db.return_game_info(callback_data['game_code'])
    await call.message.delete()
    media = types.MediaGroup()
    markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call.message.chat.id,game['game_code']), game['price'], user_id=call.message.chat.id)
    game_info_text = phr.get_product_info(game)

    for index, file_id in enumerate(game['game_cover'].split('\n')):
        match index:
            case _:
                match file_id.lower()[0]:
                    case 'b':
                        media.attach_video(video=file_id)
                    case 'a':
                        media.attach_photo(photo=file_id)


    await call.message.answer_media_group(media)
    await call.message.answer(game_info_text, reply_markup=markup)



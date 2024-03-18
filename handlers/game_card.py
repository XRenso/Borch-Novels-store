

from loader import dp,db
import keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import types
import phrase as phr
from aiogram.utils.media_group import MediaGroupBuilder
@dp.callback_query(kb.GetGameInfo_CallbackData.filter())
async def show_game_info(call:types.CallbackQuery, callback_data:kb.GetGameInfo_CallbackData):
    game = db.return_game_info(callback_data.game_code)
    markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call.message.chat.id, game['game_code']),
                         game['price'], user_id=call.message.chat.id)

    game_info_text = phr.get_product_info(game)
    try:
        await call.message.edit_text(game_info_text, reply_markup=markup.as_markup())
    except:
        try:
            await call.message.delete()
        except:
            await call.message.edit_caption('Сессия закрыта', reply_markup=None)
        await call.message.answer(game_info_text,reply_markup=markup.as_markup())

@dp.callback_query(kb.GameStatistic_CallbackData.filter())
async def show_game_statistic(call:types.CallbackQuery, callback_data:kb.GameStatistic_CallbackData):
    statistic_text = db.return_game_satistic(callback_data.game_code)
    markup = InlineKeyboardBuilder().add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=callback_data.game_code).pack()))
    try:
        await call.message.edit_text(statistic_text,reply_markup=markup.as_markup())
    except:
        await call.message.delete()
        await call.message.answer(statistic_text, reply_markup=markup.as_markup())


@dp.callback_query(kb.DeleteGameFromLibrary_CallbackData.filter())
async def delete_game_from_library(call:types.CallbackQuery, callback_data:kb.DeleteGameFromLibrary_CallbackData):
    game_code = callback_data.game_code
    markup = InlineKeyboardBuilder().add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=callback_data.game_code).pack()))
    db.delete_game_from_user_library(call.message.chat.id, game_code)
    try:
        await call.message.edit_text(phr.success_game_delete,reply_markup=markup.as_markup())
    except:
        await call.message.delete()
        await call.message.answer(phr.success_game_delete, reply_markup=markup.as_markup())

@dp.callback_query(kb.ShowMoreInfoGame_CallbackData.filter())
async def show_game_info(call:types.CallbackQuery, callback_data: kb.ShowMoreInfoGame_CallbackData):
    game = db.return_game_info(callback_data.game_code)
    await call.message.delete()
    media = MediaGroupBuilder()
    markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call.message.chat.id,game['game_code']), game['price'], user_id=call.message.chat.id)
    game_info_text = phr.get_product_info(game)

    for index, file_id in enumerate(game['game_cover'].split('\n')):
        match index:
            case _:
                match file_id.lower()[0]:
                    case 'b':
                        media.add_video(media=file_id)
                    case 'a':
                        media.add_photo(media=file_id)


    await call.message.answer_media_group(media=media.build())
    await call.message.answer(game_info_text, reply_markup=markup)


@dp.callback_query(kb.UnavailableGame_CallbackData.filter())
async def unavailable_game(call:types.CallbackQuery, callback_data: kb.UnavailableGame_CallbackData):
    game = db.return_game_info(callback_data.game_code)
    markup = InlineKeyboardBuilder()
    markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game['game_code']).pack()))
    await call.message.edit_text(f'Мы понимаем как вы хотите запустить {game["game_name"]}'
                                 f'\nОднако сейчас продукт недоступен. Наши сожаления'
                                 f'\nПодождите официального выхода', reply_markup=markup.as_markup())
from loader import dp,db
import keyboards as kb
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import phrase as phr
@dp.message_handler(commands = ['reset_game'])
async def reset_game(message:types.Message):
    markup = kb.reset_library(db.return_user_library_games(message.from_user.id))
    if not len(markup['inline_keyboard']):
        await message.answer('У вас нет игр ❌')
    else:
        await message.answer('Выберите игру, которой сбросим сохранение ', reply_markup=markup)

@dp.callback_query_handler(kb.reset_games_cb.filter())
async def confirm_reset(call:types.CallbackQuery, callback_data:dict):
    game = db.return_game_info(callback_data['game_code'])
    markup = InlineKeyboardMarkup(row_width=2)
    markup.insert(InlineKeyboardButton('Подтвердить',callback_data=kb.confirm_reset_cb.new(callback_data['game_code'])))
    markup.insert(InlineKeyboardButton('Отменить',callback_data=kb.cancel_reset_cb.new('joj')))
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_reset_cb.new('joj')))
    await call.message.edit_text(f'Уверены ли вы в сбросе сохранения игры - {game["game_name"]}?', reply_markup=markup)

@dp.callback_query_handler(kb.back_reset_cb.filter())
async def return_to_lib(call:types.CallbackQuery, callback_data:dict):
    markup = kb.reset_library(db.return_user_library_games(call.message.chat.id))
    if not len(markup['inline_keyboard']):
        await call.message.edit_text('У вас нет игр ❌')
    else:
        await call.message.edit_text('Выберите игру, которой сбросим сохранение ', reply_markup=markup)

@dp.callback_query_handler(kb.confirm_reset_cb.filter())
async def confirm_reset(call:types.CallbackQuery, callback_data:dict):
    db.reset_game_setings(user_id=call.message.chat.id, game_code=callback_data['game_code'])
    await call.message.edit_text('Успешно сброшено ✅')

@dp.callback_query_handler(kb.cancel_reset_cb.filter())
async def cancel_reset(call:types.CallbackQuery, callback_data:dict):
    await call.message.edit_text('Успешно отменено')

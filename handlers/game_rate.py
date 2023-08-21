from loader import dp,db
from aiogram import types
import keyboards as kb
import phrase as phr
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@dp.callback_query_handler(kb.rate_game.filter())
async def rating_game(call:types.CallbackQuery, callback_data:dict):
    markup = InlineKeyboardMarkup(row_width=5)
    for i in range(5):
        markup.insert(InlineKeyboardButton(f'{i+1}', callback_data=kb.rating.new(f'{callback_data["game_code"]}@{i+1}')))
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(callback_data['game_code'])))
    await call.message.edit_text('Выберите оценку', reply_markup=markup)
@dp.callback_query_handler(kb.rating.filter())
async def rate_game(call:types.CallbackQuery, callback_data:dict):
    info = callback_data['score'].split('@')
    game_code = info[0]
    score = info[1]
    db.rate_game(call.message.chat.id, game_code, score)
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(game_code)))
    await call.message.edit_text('Успешно поставлена оценка', reply_markup=markup)
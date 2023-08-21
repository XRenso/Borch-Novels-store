from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import phrase as phr

@dp.callback_query_handler(kb.get_user_group.filter())
async def get_user_group_games(call:types.CallbackQuery, callback_data:dict):
    group_name = callback_data['group_name']
    if group_name != 'Все игры':
        games = []
        for i in db.return_user_group(call.message.chat.id, group_name):
            games.append(db.return_game_info(i))
    else:
        games = db.return_user_library_games(call.message.chat.id)
    markup = kb.return_library(games)
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_to_user_group.new('ok')))
    await call.message.edit_caption(caption=f'Библиотека категория - «{group_name}»', reply_markup=markup)

@dp.callback_query_handler(kb.back_to_user_group.filter())
async def open_user_group(call:types.CallbackQuery, callback_data:dict):
    user = db.return_user_info(call.message.chat.id)
    if user:
        await call.message.edit_caption(caption='Ваша библиотека 📂', reply_markup=kb.lib_category(user['user_groups']))
from loader import dp,db
import keyboards as kb
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import phrase as phr
@dp.message_handler(commands = ['reset_game'])
async def reset_game(message:types.Message):
    user = db.return_user_info(message.from_user.id)
    text = 'Выберите игру, которой сбросим сохранение '
    if len(user['user_groups']) > 1:
        markup = kb.reset_library_categories(user['user_groups'])
        text = 'Выберите категорию игр'
    else:
        markup = kb.reset_library(db.return_user_library_games(user['user_id']))

    if not len(db.return_user_library_games(message.from_user.id)):
        await message.answer('У вас нет игр ❌')
    else:
        await message.answer(text, reply_markup=markup)

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
    user = db.return_user_info(call.message.chat.id)
    text = 'Выберите игру, которой сбросим сохранение '
    if len(user['user_groups']) > 1:
        markup = kb.reset_library_categories(user['user_groups'])
        text = 'Выберите категорию игр'
    else:
        markup = kb.reset_library(db.return_user_library_games(call.message.chat.id))

    if not len(db.return_user_library_games(call.message.chat.id)):
        await call.message.edit_text('У вас нет игр ❌')
    else:
        await call.message.edit_text(text, reply_markup=markup)

@dp.callback_query_handler(kb.confirm_reset_cb.filter())
async def confirm_reset(call:types.CallbackQuery, callback_data:dict):
    j = db.reset_game_setings(user_id=call.message.chat.id, game_code=callback_data['game_code'])
    if not j:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_reset_cb.new('ok')))
        await call.message.edit_text('Произошла ошибка.\nВидимо игры уже больше нет в вашей библиотеке\nРекомендуем удалить её из группы', reply_markup=markup)
        return
    await call.message.edit_text('Успешно сброшено ✅')

@dp.callback_query_handler(kb.cancel_reset_cb.filter())
async def cancel_reset(call:types.CallbackQuery, callback_data:dict):
    await call.message.edit_text('Успешно отменено')


@dp.callback_query_handler(kb.get_user_group_for_reset.filter())
async def show_games_from_group(call:types.CallbackQuery, callback_data:dict):
    group_name = callback_data['group_name']
    exist = True
    if group_name != 'Все игры':
        games = []
        try:
            for i in db.return_user_group(call.message.chat.id, group_name):
                games.append(db.return_game_info(i))
        except TypeError:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_to_user_group.new('ok')))
            await call.message.edit_text(f'Данной группы больше не существует. Нажмите назад, чтобы вернуться в библиотеку', reply_markup=markup)
            exist = False
    else:
        games = db.return_user_library_games(call.message.chat.id)
    if exist:
        markup = kb.reset_library(games)
        markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_reset_cb.new('ok')))
        await call.message.edit_text(text=f'Выберите игру из категории «{group_name}»\nЧтобы удалить ей сохранение', reply_markup=markup)
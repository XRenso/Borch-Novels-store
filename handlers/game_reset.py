from loader import dp,db
import keyboards as kb
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
import phrase as phr
from aiogram.filters.command import Command
@dp.message(Command('reset_game'))
async def reset_game(message:types.Message):
    user = db.return_user_info(message.from_user.id)
    text = 'Выберите игру, которой сбросим сохранение'
    if len(user['user_groups']) > 1:
        markup = kb.reset_library_categories(user['user_groups'])
        text = 'Выберите категорию игр'
    else:
        markup = kb.reset_library(db.return_user_library_games(user['user_id']))

    if not len(db.return_user_library_games(message.from_user.id)):
        await message.answer('У вас нет игр ❌')
    else:
        await message.answer(text, reply_markup=markup.as_markup())

@dp.callback_query(kb.ResetGame_CallbackData.filter())
async def confirm_reset(call:types.CallbackQuery, callback_data:kb.ResetGame_CallbackData):
    game = db.return_game_info(callback_data['game_code'])
    markup = InlineKeyboardBuilder()
    btn = []
    btn.append(InlineKeyboardButton(text='Подтвердить',callback_data=kb.ConfirmResetGame_CallbackData(game_code=callback_data['game_code']).pack()))
    btn.append(InlineKeyboardButton(text='Отменить',callback_data=kb.CancelResetGame_CallbackData(ok='joj').pack()))
    markup.row(*btn,width=2)
    markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackResetGame_CallbackData(ok='joj').pack()))
    await call.message.edit_text(f'Уверены ли вы в сбросе сохранения игры - {game["game_name"]}?', reply_markup=markup.as_markup())

@dp.callback_query(kb.BackResetGame_CallbackData.filter())
async def return_to_lib(call:types.CallbackQuery, callback_data:kb.BackResetGame_CallbackData):
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
        await call.message.edit_text(text, reply_markup=markup.as_markup())

@dp.callback_query(kb.ConfirmResetGame_CallbackData.filter())
async def confirm_reset(call:types.CallbackQuery, callback_data:kb.ConfirmResetGame_CallbackData):
    j = db.reset_game_setings(user_id=call.message.chat.id, game_code=callback_data.game_code)
    if j == 0:
        markup = InlineKeyboardBuilder()
        markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackResetGame_CallbackData(ok='ok').pack()))
        await call.message.edit_text('Произошла ошибка.\nВидимо игры уже больше нет в вашей библиотеке\nРекомендуем удалить её из группы', reply_markup=markup.as_markup())
        return
    await call.message.edit_text('Успешно сброшено ✅')

@dp.callback_query(kb.CancelResetGame_CallbackData.filter())
async def cancel_reset(call:types.CallbackQuery, callback_data:kb.CancelResetGame_CallbackData):
    await call.message.edit_text('Успешно отменено')


@dp.callback_query(kb.GetUserGroupForReset_CallbackData.filter())
async def show_games_from_group(call:types.CallbackQuery, callback_data:kb.GetUserGroupForReset_CallbackData):
    group_name = callback_data.group_name
    exist = True
    if group_name != 'Все игры':
        games = []
        try:
            for i in db.return_user_group(call.message.chat.id, group_name):
                games.append(db.return_game_info(i))
        except TypeError:
            markup = InlineKeyboardBuilder()
            markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackResetGame_CallbackData(ok='ok').pack()))
            await call.message.edit_text(f'Данной группы больше не существует. Нажмите назад, чтобы вернуться назад', reply_markup=markup.as_markup())
            exist = False
    else:
        games = db.return_user_library_games(call.message.chat.id)
    if exist:
        markup = kb.reset_library(games)
        markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackResetGame_CallbackData(ok='ok').pack()))
        await call.message.edit_text(text=f'Выберите игру из категории «{group_name}»\nЧтобы удалить ей сохранение', reply_markup=markup.as_markup())
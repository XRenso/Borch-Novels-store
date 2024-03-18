from loader import dp,db
import keyboards as kb
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardButton, KeyboardButton)
from aiogram import types
import phrase as phr
from states.Store import Store
from aiogram.fsm.context import FSMContext
@dp.callback_query(kb.GetUserGroup_CallbackData.filter())
async def get_user_group_games(call:types.CallbackQuery, callback_data:kb.GetUserGroup_CallbackData):
    group_name = callback_data.group_name
    page = int(callback_data.page)
    exist = True
    if group_name != 'Все игры':
        games = []
        try:
            for i in db.return_user_group(call.message.chat.id, group_name):
                games.append(db.return_game_info(i))
        except TypeError:
            markup = InlineKeyboardBuilder()
            markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackToUserGroup_CallbackData(back='ok').pack()))
            await call.message.edit_caption(f'Данной группы больше не существует. Нажмите назад, чтобы вернуться в библиотеку', reply_markup=markup.as_markup())
            exist = False
    else:
        games = db.return_user_library_games(call.message.chat.id)
    if exist:
        markup = kb.return_library(games, page=page, category_code=group_name)
        markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackToUserGroup_CallbackData(back='ok').pack()))
        await call.message.edit_caption(caption=f'Библиотека категория - «{group_name}»', reply_markup=markup.as_markup())

@dp.callback_query(kb.BackToUserGroup_CallbackData.filter())
async def open_user_group(call:types.CallbackQuery, callback_data:kb.BackToUserGroup_CallbackData):
    user = db.return_user_info(call.message.chat.id)
    if user:
        await call.message.edit_caption(caption='Ваша библиотека 📂', reply_markup=kb.lib_category(user['user_groups']).as_markup())

@dp.callback_query(kb.ControlUserGroup_CallbackData.filter())
async def control_user_group(call:types.CallbackQuery, callback_data:kb.ControlUserGroup_CallbackData):
    game_code = callback_data.game_code
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text=phr.add_to_user_group, callback_data=kb.AddToUserGroup_CallbackData(game_code=game_code).pack()))
    markup.row(InlineKeyboardButton(text=phr.remove_from_user_group, callback_data=kb.RemoveFromUserGroup_CallbackData(game_code=game_code).pack()))
    markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game_code).pack()))
    await call.message.edit_text(f'Выберите действие', reply_markup=markup.as_markup())

@dp.callback_query(kb.AddToUserGroup_CallbackData.filter())
async def add_game_to_user_group(call:types.CallbackQuery, callback_data:kb.AddToUserGroup_CallbackData):
    game_code = callback_data.game_code
    groups = db.get_user_group_by_game(call.message.chat.id, game_code, 1)
    markup = InlineKeyboardBuilder()
    for i in groups:
        markup.row(InlineKeyboardButton(text=i, callback_data=kb.ChooseGroupAdd_CallbackData(game_code=game_code,group_name=i).pack()))

    markup.row(InlineKeyboardButton(text='Создать новую группу',callback_data=kb.CreateNewUserGroup_CallbackData(game_code=game_code).pack()))
    markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.ControlUserGroup_CallbackData(game_code=game_code).pack()))
    await call.message.edit_text(f'Выберите группу, куда добавить игру', reply_markup=markup.as_markup())
@dp.callback_query(kb.ChooseGroupAdd_CallbackData.filter())
async def choose_group_add(call:types.CallbackQuery, callback_data:kb.ChooseGroupAdd_CallbackData):
    group_name = callback_data.group_name
    game_code = callback_data.game_code
    db.create_user_group(call.message.chat.id,group_name, game_code)
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game_code).pack()))
    await call.message.edit_text(f'Успешно добавлено в группу {group_name}', reply_markup=markup.as_markup())

@dp.callback_query(kb.RemoveFromUserGroup_CallbackData.filter())
async def remove_from_user_group(call:types.CallbackQuery, callback_data:kb.RemoveFromUserGroup_CallbackData):
    game_code = callback_data.game_code
    groups = db.get_user_group_by_game(call.message.chat.id, game_code,0)
    markup = InlineKeyboardBuilder()
    if groups:
        for i in groups:
            markup.row(InlineKeyboardButton(text=i, callback_data=kb.ChooseGroupRemove_CallbackData(game_code=game_code, group_name=i).pack()))

        markup.row(InlineKeyboardButton(text='Из всех групп', callback_data=kb.ChooseGroupRemove_CallbackData(game_code=game_code, group_name='__NONE__').pack()))
        if db.check_is_game_in_user_library(call.message.chat.id, game_code):
            markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.ControlUserGroup_CallbackData(game_code=game_code).pack()))
        else:
            markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game_code).pack()))
        await call.message.edit_text(f'Выберите группу из которой нужно удалить продукт', reply_markup=markup.as_markup())
    else:
        if db.check_is_game_in_user_library(call.message.chat.id, game_code):
            markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.ControlUserGroup_CallbackData(game_code=game_code).pack()))
        else:
            markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game_code).pack()))
        await call.message.edit_text(f'У вас нет групп, из которых можно удалить продукт', reply_markup=markup.as_markup())


@dp.callback_query(kb.ChooseGroupRemove_CallbackData.filter())
async def choose_group_remove(call:types.CallbackQuery, callback_data:kb.ChooseGroupRemove_CallbackData):
    group_name = callback_data.group_name
    game_code = callback_data.game_code
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game_code).pack()))
    if group_name != '__NONE__':
        db.delete_game_from_group(call.message.chat.id,group_name, game_code)
        await call.message.edit_text(f'Успешно удалено из группы {group_name}', reply_markup=markup.as_markup())
        group = db.return_user_group(call.message.chat.id, group_name)
        if group is not None:
            if not group:
                db.delete_user_group(call.message.chat.id, group_name)
    else:
        groups = db.get_user_group_by_game(call.message.chat.id, game_code, 0)
        for i in groups:
            db.delete_game_from_group(call.message.chat.id, i, game_code)
            group = db.return_user_group(call.message.chat.id, i)
            if group is not None:
                if not group:
                    db.delete_user_group(call.message.chat.id, i)
        await call.message.edit_text(f'Игра успешно удалена из всех групп', reply_markup=markup.as_markup())

@dp.callback_query(kb.CreateNewUserGroup_CallbackData.filter())
async def create_user_group(call:types.CallbackQuery, callback_data:kb.CreateNewUserGroup_CallbackData, state:FSMContext):
    await call.message.edit_text(f'Отправьте название новой группы')
    await state.update_data(game_code_for_group=callback_data.game_code)
    await state.set_state(Store.create_user_group)


@dp.message(Store.create_user_group)
async def create_user_group(message: types.Message, state: FSMContext):
    group_name = message.text
    data = await state.get_data()
    markup = InlineKeyboardBuilder()
    markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=data["game_code_for_group"]).pack()))
    if message.text != '/cancel':
        if len(group_name) <=20:
            db.create_user_group(message.from_user.id, group_name,data['game_code_for_group'])
            game = db.return_game_info(data["game_code_for_group"])
            await message.answer(f'«{game["game_name"]}» успешно добавлено в «{group_name}»', reply_markup=markup.as_markup())
            await state.clear()
        else:
            await message.answer(f'Название слишком длинное. Оно должно быть не больше 20 символов')
    else:
        await message.answer(f'Успешно отменено', reply_markup=markup.as_markup())
        await state.clear()
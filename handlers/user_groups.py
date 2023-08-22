from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import phrase as phr
from states.Store import Store
from aiogram.dispatcher import FSMContext
@dp.callback_query_handler(kb.get_user_group.filter())
async def get_user_group_games(call:types.CallbackQuery, callback_data:dict):
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
            await call.message.edit_caption(f'Данной группы больше не существует. Нажмите назад, чтобы вернуться в библиотеку', reply_markup=markup)
            exist = False
    else:
        games = db.return_user_library_games(call.message.chat.id)
    if exist:
        markup = kb.return_library(games)
        markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_to_user_group.new('ok')))
        await call.message.edit_caption(caption=f'Библиотека категория - «{group_name}»', reply_markup=markup)

@dp.callback_query_handler(kb.back_to_user_group.filter())
async def open_user_group(call:types.CallbackQuery, callback_data:dict):
    user = db.return_user_info(call.message.chat.id)
    if user:
        await call.message.edit_caption(caption='Ваша библиотека 📂', reply_markup=kb.lib_category(user['user_groups']))

@dp.callback_query_handler(kb.control_user_group.filter())
async def control_user_group(call:types.CallbackQuery, callback_data:dict):
    game_code = callback_data['game_code']
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(phr.add_to_user_group, callback_data=kb.add_to_user_group.new(game_code)))
    markup.add(InlineKeyboardButton(phr.remove_from_user_group, callback_data=kb.remove_from_user_group.new(game_code)))
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(game_code)))
    await call.message.edit_text(f'Выберите действие', reply_markup=markup)

@dp.callback_query_handler(kb.add_to_user_group.filter())
async def add_game_to_user_group(call:types.CallbackQuery, callback_data:dict):
    game_code = callback_data['game_code']
    groups = db.get_user_group_by_game(call.message.chat.id, game_code, 1)
    print(groups)
    markup = InlineKeyboardMarkup()
    for i in groups:
        markup.add(InlineKeyboardButton(i, callback_data=kb.choose_group_add.new(game_code,i)))

    markup.add(InlineKeyboardButton('Создать новую группу',callback_data=kb.create_new_user_group.new(game_code)))
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.control_user_group.new(game_code)))
    await call.message.edit_text(f'Выберите группу, куда добавить игру', reply_markup=markup)
@dp.callback_query_handler(kb.choose_group_add.filter())
async def choose_group_add(call:types.CallbackQuery, callback_data:dict):
    group_name = callback_data['group_name']
    game_code = callback_data['game_code']
    db.create_user_group(call.message.chat.id,group_name, game_code)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(game_code)))
    await call.message.edit_text(f'Успешно добавлено в группу {group_name}', reply_markup=markup)

@dp.callback_query_handler(kb.remove_from_user_group.filter())
async def remove_from_user_group(call:types.CallbackQuery, callback_data:dict):
    game_code = callback_data['game_code']
    groups = db.get_user_group_by_game(call.message.chat.id, game_code,0)
    markup = InlineKeyboardMarkup()
    if groups:
        for i in groups:
            markup.add(InlineKeyboardButton(i, callback_data=kb.choose_group_remove.new(game_code, i)))

        markup.add(InlineKeyboardButton('Из всех групп', callback_data=kb.choose_group_remove.new(game_code, '__NONE__')))
        if db.check_is_game_in_user_library(call.message.chat.id, game_code):
            markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.control_user_group.new(game_code)))
        else:
            markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(game_code)))
        await call.message.edit_text(f'Выберите группу из которой нужно удалить продукт', reply_markup=markup)
    else:
        if db.check_is_game_in_user_library(call.message.chat.id, game_code):
            markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.control_user_group.new(game_code)))
        else:
            markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(game_code)))
        await call.message.edit_text(f'У вас нет групп, из которых можно удалить продукт', reply_markup=markup)


@dp.callback_query_handler(kb.choose_group_remove.filter())
async def choose_group_remove(call:types.CallbackQuery, callback_data:dict):
    group_name = callback_data['group_name']
    game_code = callback_data['game_code']
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(game_code)))
    if group_name != '__NONE__':
        db.delete_game_from_group(call.message.chat.id,group_name, game_code)
        await call.message.edit_text(f'Успешно удалено из группы {group_name}', reply_markup=markup)
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
        await call.message.edit_text(f'Игра успешно удалена из всех групп', reply_markup=markup)

@dp.callback_query_handler(kb.create_new_user_group.filter(), state='*')
async def create_user_group(call:types.CallbackQuery, callback_data:dict, state:FSMContext):
    await call.message.edit_text(f'Отправьте название новой группы')
    await state.update_data(game_code_for_group=callback_data['game_code'])
    await Store.create_user_group.set()


@dp.message_handler(state=Store.create_user_group)
async def create_user_group(message: types.Message, state: FSMContext):
    group_name = message.text
    data = await state.get_data()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(data["game_code_for_group"])))
    if message.text != '/cancel':
        if len(group_name) <=20:
            db.create_user_group(message.from_user.id, group_name,data['game_code_for_group'])
            game = db.return_game_info(data["game_code_for_group"])
            await message.answer(f'«{game["game_name"]}» успешно добавлено в «{group_name}»', reply_markup=markup)
            await state.finish()
        else:
            await message.answer(f'Название слишком длинное. Оно должно быть не больше 20 символов')
    else:
        await message.answer(f'Успешно отменено', reply_markup=markup)
        await state.finish()
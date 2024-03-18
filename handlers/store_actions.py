from loader import dp,db
from states.Store import Store
from aiogram import types
from aiogram.fsm.context import FSMContext
import keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
import phrase as phr

@dp.message(Store.goto_page)
async def going_to_page(message: types.Message, state: FSMContext):
    page = message.text
    if page != '/cancel':
        try:
            page = int(page)
        except ValueError:
            await message.answer('Введите только число ❌')
        user = db.return_user_info(message.from_user.id)
        game_code = user['curr_game_code']
        num_of_pages = db.return_number_of_frames(game_code)
        markup = InlineKeyboardBuilder().add(
            InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.PlayingGame_CallbackData(game_code=game_code).pack()))

        if page in range(1, num_of_pages+1):
            db.update_user_frame_num(user['user_id'],page, game_code)
            await message.answer('Страница успешно сменена', reply_markup=markup.as_markup())
            await state.clear()

        else:
            if type(page) is int:
                await message.answer('Неверный диапозон страницы ❌')
    else:
        user = db.return_user_info(message.from_user.id)
        game_code = user['curr_game_code']
        markup = InlineKeyboardBuilder().add(
            InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.PlayingGame_CallbackData(game_code=game_code).pack()))
        await message.answer('Успешно отменено ✅', reply_markup=markup.as_markup())
        await state.clear()

@dp.message(Store.search_game)
async def search_game_by_name(message: types.Message, state: FSMContext):
    search = message.text
    if search != '/cancel':
        games = db.search_game_by_name(search)
        markup = kb.return_library(games)
        if not len(markup.as_markup().inline_keyboard):
            await message.answer(f'К сожалению у нас нет игр по запросу {search} 😕\nВы можете попробовать ещё раз, написав снова название, либо завершить поиск с пощью команды /cancel')
        else:
            await message.answer(f'Результат поиска по запросу {search}:', reply_markup=markup.as_markup())
            await state.clear()
    else:
        await message.answer('Успешная отмена ❌')
        await state.clear()


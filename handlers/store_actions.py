from loader import dp,db
from states.Store import Store
from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import phrase as phr

@dp.message_handler(state=Store.goto_page)
async def going_to_page(message: types.Message, state: FSMContext):
    page = message.text
    try:
        page = int(page)
    except ValueError:
        await message.answer('Введите только число ❌')
    user = db.return_user_info(message.from_user.id)
    game_code = user['curr_game_code']
    num_of_pages = db.return_number_of_frames(game_code)
    markup = InlineKeyboardMarkup().add(
        InlineKeyboardButton(phr.back_to_game, callback_data=kb.play_game.new(f'{game_code}')))

    if page in range(1, num_of_pages+1):
        db.update_user_frame_num(user['user_id'],page, game_code)
        await message.answer('Страница успешно сменена', reply_markup=markup)
        await state.finish()
    elif page == 0:
        await message.answer('Успешно отменено ✅', reply_markup=markup)
        await state.finish()

    else:
        if type(page) is int:
            await message.answer('Неверный диапозон страницы ❌')
@dp.message_handler(state=Store.search_game)
async def search_game_by_name(message: types.Message, state: FSMContext):
    search = message.text
    if search != '0':
        games = db.search_game_by_name(search)
        markup = kb.return_library(games)
        if not len(markup['inline_keyboard']):
            await message.answer(f'К сожалению у нас нет игр по запросу {search} 😕')
        else:
            await message.answer(f'Результат поиска по запросу {search}:', reply_markup=markup)
    else:
        await message.answer('Успешная отмена ❌')
    await state.finish()


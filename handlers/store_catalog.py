from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardButton
from aiogram import types
import phrase as phr
from aiogram.types import InputMediaPhoto


@dp.callback_query_handler(kb.show_more_game_genre.filter())
async def get_games_by_genre(call:types.CallbackQuery, callback_data: dict):
    info = callback_data['genre_code'].split('@')
    type_code = info[0]
    genre_code = info[1]
    markup = kb.return_library(db.return_game_by_genre(genre_code, type_code)).add(InlineKeyboardButton('Назад ↩️', callback_data=kb.store_action.new(f'{type_code}@go_to_genres')))
    content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Товары жанра {db.return_genre_name_by_code(genre_code, type_code)}:')
    await call.message.edit_media(content,reply_markup=markup)

@dp.callback_query_handler(kb.show_genres_by_type.filter())
async def get_genres_by_type(call:types.CallbackQuery, callback_data: dict):
    type_code = callback_data['type_code']
    genres = db.return_genres(type_code)
    markup = kb.store_kb_genres(genres, type_code)
    back_to_types = InlineKeyboardButton(phr.back_to_game, callback_data=kb.store_action.new(f'{type_code}@go_to_types'))
    markup.add(back_to_types)
    if not len(markup['inline_keyboard']):
        await call.message.edit_caption(f'Игры отсутствуют в магазине ❌')
    else:
        await call.message.edit_caption(f'Выберите интересующий вас жанр 👇', reply_markup=markup)

@dp.callback_query_handler(kb.store_action.filter())
async def store_handler(call:types.CallbackQuery, callback_data: dict):
    info = callback_data['action'].split('@')
    action = info[1]
    type_code = info[0]
    match action:
        case 'go_to_genres':
            genres = db.return_genres(type_code)
            back_to_types = InlineKeyboardButton(phr.back_to_game,
                                                 callback_data=kb.store_action.new(f'{type_code}@go_to_types'))
            markup = kb.store_kb_genres(genres, type_code)
            markup.add(back_to_types)
            content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Выберите интересующую вас жанр 👇')
            await call.message.edit_media(content, reply_markup=markup)
        case 'go_to_types':
            types = db.return_type()
            markup = kb.store_kb_types(types)
            if not len(markup['inline_keyboard']):
                await call.message.edit_text(f'Отсутствует товар в магазине ❌')
            else:
                content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Выберите интересующую вас категорию 👇')
                await call.message.edit_media(content, reply_markup=markup)

@dp.callback_query_handler(kb.unavailable_game.filter())
async def unavailable_game(call:types.CallbackQuery, callback_data: dict):
    game = db.return_game_info(callback_data['game_code'])
    await call.message.edit_text(f'Мы понимаем как вы хотите поиграть в {game["game_name"]}'
                                 f'\nОднако сейчас игра недоступна. Наши сожаления'
                                 f'\nПодождите официального выхода')

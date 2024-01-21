from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import types
import phrase as phr
from aiogram.types import InputMediaPhoto


@dp.callback_query_handler(kb.show_more_game_genre.filter())
async def get_games_by_genre(call:types.CallbackQuery, callback_data: dict):

    type_code = callback_data['type_code']
    genre_code = callback_data['genre_code']
    page = int(callback_data['page'])
    markup = kb.return_library(db.return_game_by_genre(genre_code, type_code), type='store',page=page, type_code=type_code, category_code=genre_code).add(InlineKeyboardButton('Назад ↩️', callback_data=kb.store_action.new(f'{type_code}@go_to_genres')))
    content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Товары жанра {db.return_genre_name_by_code(genre_code, type_code)}:')
    await call.message.edit_media(content,reply_markup=markup)

@dp.callback_query_handler(kb.end_list.filter())
async def list_is_end(call:types.CallbackQuery, callback_data: dict):
    await call.answer('Дальше ничего нет', show_alert=False)

@dp.callback_query_handler(kb.get_all_pages.filter())
async def change_page_of_group(call:types.CallbackQuery, callback_data: dict):
    type = callback_data['type']
    category_code = callback_data['category_code']
    type_code = None
    match type:
        case 'store':
            type_code = callback_data['type_code']
    markup = InlineKeyboardMarkup(row_width=5)
    if type_code:
        games = db.return_game_by_genre(category_code, type_code)
        pages = len(games)//5
        if len(games)%5 != 0:
            pages+=1
        for i in range(1,pages+1):
            markup.insert(InlineKeyboardButton(f'{i}',callback_data=kb.show_more_game_genre.new(type_code,category_code,str(i-1))))
        content = InputMediaPhoto(
            media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ',
            caption=f'Товары жанра {db.return_genre_name_by_code(category_code, type_code)}\nВыберите страницу:')
        await call.message.edit_media(content,reply_markup=markup)
    else:

        if category_code != 'Все игры':
            games = []
            try:
                for i in db.return_user_group(call.message.chat.id, category_code):
                    games.append(db.return_game_info(i))

            except TypeError:
                markup = InlineKeyboardMarkup()
                markup.insert(InlineKeyboardButton(phr.back_to_game, callback_data=kb.back_to_user_group.new('ok')))
                await call.message.edit_caption(
                    f'Данной группы больше не существует. Нажмите назад, чтобы вернуться в библиотеку',
                    reply_markup=markup)
            if games:
                pages = len(games) // 5
                if len(games) % 5 != 0:
                    pages += 1
                for i in range(1,pages+1):
                    markup.insert(InlineKeyboardButton(f'{i}',
                                                    callback_data=kb.get_user_group.new(category_code,
                                                                                              str(i - 1))))
                await call.message.edit_caption(caption=f'Библиотека категория - «{category_code}»\nВыберите страницу:', reply_markup=markup)
        else:
            games = db.return_user_library_games(call.message.chat.id)
            pages = len(games) // 5
            if len(games) % 5 != 0:
                pages += 1
            for i in range(1, pages + 1):
                markup.insert(InlineKeyboardButton(f'{i}',
                                                callback_data=kb.get_user_group.new(category_code,
                                                                                    str(i - 1))))
            await call.message.edit_caption(caption=f'Библиотека категория - «{category_code}»\nВыберите страницу:', reply_markup=markup)

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



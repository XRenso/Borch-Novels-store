from loader import dp,db
import keyboards as kb
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardButton, KeyboardButton)
from aiogram import types
import phrase as phr
from aiogram.types import InputMediaPhoto


@dp.callback_query(kb.ShowMoreGameGenre_CallbackData.filter())
async def get_games_by_genre(call:types.CallbackQuery, callback_data: kb.ShowMoreGameGenre_CallbackData):

    type_code = callback_data.type_code
    genre_code = callback_data.genre_code
    page = int(callback_data.page)
    markup = kb.return_library(db.return_game_by_genre(genre_code, type_code), type='store',page=page, type_code=type_code, category_code=genre_code).add(InlineKeyboardButton(text='Назад ↩️', callback_data=kb.StoreAction_CallbackData(type_code=type_code,action='go_to_genres').pack()))
    content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Товары жанра {db.return_genre_name_by_code(genre_code, type_code)}:')
    await call.message.edit_media(content,reply_markup=markup.as_markup())

@dp.callback_query(kb.EndList_CallbackData.filter())
async def list_is_end(call:types.CallbackQuery, callback_data: kb.EndList_CallbackData):
    await call.answer('Дальше ничего нет', show_alert=False)

@dp.callback_query(kb.GetAllPages_CallbackData.filter())
async def change_page_of_group(call:types.CallbackQuery, callback_data: kb.GetAllPages_CallbackData):
    type = callback_data.type
    category_code = callback_data.category_code
    type_code = None
    match type:
        case 'store':
            type_code = callback_data.type_code
    markup = InlineKeyboardBuilder()
    btn = []
    if type_code:
        games = db.return_game_by_genre(category_code, type_code)
        pages = len(games)//5
        if len(games)%5 != 0:
            pages+=1
        for i in range(1,pages+1):
            btn.append(InlineKeyboardButton(text=f'{i}',callback_data=kb.ShowMoreGameGenre_CallbackData(type_code=type_code,genre_code=category_code,page=i-1).pack()))
        markup.row(*btn,width=5)
        content = InputMediaPhoto(
            media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ',
            caption=f'Товары жанра {db.return_genre_name_by_code(category_code, type_code)}\nВыберите страницу:')
        await call.message.edit_media(content,reply_markup=markup.as_markup())
    else:

        if category_code != 'Все игры':
            games = []
            try:
                for i in db.return_user_group(call.message.chat.id, category_code):
                    games.append(db.return_game_info(i))

            except TypeError:
                markup = InlineKeyboardBuilder()
                markup.add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.BackToUserGroup_CallbackData(back='ok').pack()))
                await call.message.edit_caption(
                    f'Данной группы больше не существует. Нажмите назад, чтобы вернуться в библиотеку',
                    reply_markup=markup.as_markup())
            if games:
                pages = len(games) // 5
                if len(games) % 5 != 0:
                    pages += 1
                for i in range(1,pages+1):
                    markup.add(InlineKeyboardButton(text=f'{i}',
                                                    callback_data=kb.GetUserGroup_CallbackData(group_name=category_code,
                                                                                              page=i - 1).pack()))
                await call.message.edit_caption(caption=f'Библиотека категория - «{category_code}»\nВыберите страницу:', reply_markup=markup.as_markup())
        else:
            games = db.return_user_library_games(call.message.chat.id)
            pages = len(games) // 5
            if len(games) % 5 != 0:
                pages += 1
            for i in range(1, pages + 1):
                markup.add(InlineKeyboardButton(text=f'{i}',
                                                callback_data=kb.GetUserGroup_CallbackData(group_name=category_code,
                                                                                    page=i-1).pack()))
            await call.message.edit_caption(caption=f'Библиотека категория - «{category_code}»\nВыберите страницу:', reply_markup=markup.as_markup())

@dp.callback_query(kb.ShowGenresByType_CallbackData.filter())
async def get_genres_by_type(call:types.CallbackQuery, callback_data: kb.ShowGenresByType_CallbackData):
    type_code = callback_data.type_code
    genres = db.return_genres(type_code)
    markup = kb.store_kb_genres(genres, type_code)
    back_to_types = InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.StoreAction_CallbackData(type_code=type_code,action='go_to_types').pack())
    markup.add(back_to_types)
    if not len(markup.as_markup().inline_keyboard):
        await call.message.edit_caption(caption=f'Игры отсутствуют в магазине ❌')
    else:
        await call.message.edit_caption(caption=f'Выберите интересующий вас жанр 👇', reply_markup=markup.as_markup())

@dp.callback_query(kb.StoreAction_CallbackData.filter())
async def store_handler(call:types.CallbackQuery, callback_data: kb.StoreAction_CallbackData):
    action = callback_data.action
    type_code = callback_data.type_code
    match action:
        case 'go_to_genres':
            genres = db.return_genres(type_code)
            back_to_types = InlineKeyboardButton(text=phr.back_to_game,
                                                 callback_data=kb.StoreAction_CallbackData(type_code=type_code,action='go_to_types').pack())
            markup = kb.store_kb_genres(genres, type_code)
            markup.row(back_to_types)
            content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Выберите интересующую вас жанр 👇')
            await call.message.edit_media(content, reply_markup=markup.as_markup())
        case 'go_to_types':
            types = db.return_type()
            markup = kb.store_kb_types(types)
            if not len(markup.as_markup().inline_keyboard):
                await call.message.edit_text(text=f'Отсутствует товар в магазине ❌')
            else:
                content = InputMediaPhoto(media='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ', caption=f'Выберите интересующую вас категорию 👇')
                await call.message.edit_media(content, reply_markup=markup.as_markup())



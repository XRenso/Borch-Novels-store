import random

import aiogram.utils.exceptions
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio
from aiogram.contrib.fsm_storage.memory import MemoryStorage



from database import Mongo as mg
import keyboards as kb
from dotenv import load_dotenv
import os
import logging
import phrase as phr


storage=MemoryStorage()
load_dotenv()
bot = Bot(token = os.getenv('TOKEN'))
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot=bot,storage=storage)

db = mg()
db.__init__()






class Store(StatesGroup):
    search_game = State()




@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    db.add_user(message.from_user.id)
    await message.answer(f'Здравствуй, {message.from_user.first_name}!'
                            f'\nДобро пожаловать в магазин Borch Novels.', reply_markup=kb.main_kb)


@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_photo = message.photo[-1].file_id
        await message.answer_photo(id_photo,caption=id_photo)
@dp.message_handler(content_types=['video'])
async def handle_photo(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_video = message.video.file_id
        await message.answer_video(id_video,caption=id_video)
@dp.message_handler(content_types=['sticker'])
async def handle_photo(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_sticker = message.sticker.file_id
        await message.answer_sticker(id_sticker)
        await message.answer(id_sticker)
@dp.message_handler(content_types=['audio'])
async def handle_photo(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_audio = message.audio.file_id
        await message.answer_audio(id_audio,caption=id_audio)



async def reset_cur_game(message:types.Message):
    user = db.return_user_info(message.from_user.id)
    db.update_user_frame_num(message.from_user.id, 1,user['curr_game_code'])
    await message.answer('Успешно сброшено')


@dp.message_handler(content_types=['text'])
async def get_text(message: types.Message):
    match message.text:
        case phr.library:
            markup = kb.return_library(db.return_user_library_games(message.from_user.id))
            if not len(markup['inline_keyboard']):
                await message.answer('У вас нет игр')
            else:
                await message.answer('Ваша библиотека', reply_markup=markup)
        case phr.profile:
            user_info = db.return_user_info(message.from_user.id)
            curr_game = db.return_game_info(user_info['curr_game_code'])
            if curr_game == 0:
                curr_game = 'К сожалению вы не проходите сейчас какую-либо игру'
            else:
                curr_game = curr_game['game_name']
            achivments = user_info['achivements']
            if len(achivments) < 1:
                achivments = 'У вас нет достижений'

            await message.answer(f'Ваш id - {user_info["user_id"]}'
                                 f'\nКоличество игр в библиотеке - {len(db.return_user_library_games(message.from_user.id))}'
                                 f'\nВы проходите - {curr_game}'
                                 f'\nВаши достижения:'
                                 f'\n{achivments}')
        case phr.search_game:
            await message.answer('Отправьте название игры, которую хотите найти. \nОтправьте 0 для отмены')
            await Store.search_game.set()


        case phr.store:
            genres = db.return_genres()
            markup = kb.store_kb_genres(genres)
            if not len(markup['inline_keyboard']):
                await message.answer(f'Игры отсутсвуют в магазине')
            else:
                await message.answer(f'Выберите интересующую вас категорию', reply_markup=markup)
        case phr.shop:
            await message.answer('Выберите интересующую вас функцию', reply_markup=kb.shop_kb)
        case phr.main_menu:
            await message.answer('Добро пожаловать на главное меню', reply_markup=kb.main_kb)

@dp.message_handler(state=Store.search_game)
async def search_game_by_name(message: types.Message, state: FSMContext):
    search = message.text
    if search != '0':
        games = db.search_game_by_name(search)
        markup = kb.return_library(games)
        if not len(markup['inline_keyboard']):
            await message.answer(f'К сожалению у нас нет игр по запросу {search}')
        else:
            await message.answer(f'Результат поиска по запросу {search}:', reply_markup=markup)
    else:
        await message.answer('Успешная отмена')
    await state.finish()



# async def start_battle(call: types.CallbackQuery, state: FSMContext):
#     data = await state.get_data()
#     if call.data.startswith('frame') or call.data.endswith('frame'):
#         await state.update_data(frame=call)
#     if data.get('enemy') == None:
#         async with state.proxy():
#             enemy = enemy_generator.create_monster()
#             await state.update_data(enemy=enemy)
#             data = await state.get_data()
#     enemy = data.get('enemy')
#     last_action = 'Ничего не произошло'
#     await call.message.answer(f'Враг - {enemy.get_stat("name")}'
#                          f'\nРаса - {enemy.get_stat("race")}'
#                          f'\nРодом из - {enemy.get_stat("country")}'
#                          f'\nВозраст - {enemy.get_stat("age")}'
#                          f'\nЗдоровье - {enemy.get_stat("hp")}'
#                          f'\n#######'
#                          f'\n{last_action}'
#                          f'\n#########'
#                          f'\nВаше здоровье - {db.return_user_info(call.message.chat.id)["hp"]}',reply_markup=kb.battle_kb)

# async def continue_battle(call, state):
#     cb_data = call.data
#     data = await state.get_data()
#     enemy = data.get('enemy')
#     enemy_move = random.randrange(2)
#     last_en_action = 'Ничего не произошло'
#     if cb_data.startswith('punch'):
#         user_dmg = db.return_user_info(call.message.chat.id)['dmg']
#         enemy.get_damage(random.randrange(user_dmg // 2, user_dmg + 1))
#     elif cb_data.startswith('heal'):
#         db.user_health(call.message.chat.id, random.randrange(1, db.return_user_info(call.message.chat.id)['hp']))
#     match enemy_move:
#         case 1:
#             last_en_action = db.user_get_dmg(call.message.chat.id, enemy.attack())
#         case 0:
#             last_en_action = enemy.health()
#     await state.update_data(enemy=enemy)
#     if db.return_user_info(call.message.chat.id)['hp'] == 0 and not enemy.dead():
#         await call.message.answer_sticker('CAACAgEAAxkBAAIDimR_1TToDteE_e_htszvUey4rLOgAAIHAAPJd9FOnQpx5SSzvvQvBA')
#         await call.message.edit_text('Вы погибли. Земля водой')
#         await state.reset_state()
#         db.change_user_state(call.message.chat.id,0)
#     elif enemy.dead() and db.return_user_info(call.message.chat.id)['hp'] == 0:
#         await call.message.answer_sticker('CAACAgEAAxkBAAIDimR_1TToDteE_e_htszvUey4rLOgAAIHAAPJd9FOnQpx5SSzvvQvBA')
#         await call.message.edit_text('Вы оба погибли. Водичка')
#         await state.reset_state()
#         db.change_user_state(call.message.chat.id,0)
#     elif enemy.dead() and db.return_user_info(call.message.chat.id)['hp'] != 0:
#         await call.message.edit_text('Вы победили. Сыр маслом')
#         await state.reset_state()
#         db.change_user_state(call.message.chat.id, 0)
#         await change_frames(data.get('frame'), state)
#
#     else:
#         try:
#             await call.message.edit_text(f'Враг - {enemy.get_stat("name")}'
#                                          f'\nРаса - {enemy.get_stat("race")}'
#                                          f'\nРодом из - {enemy.get_stat("country")}'
#                                          f'\nВозраст - {enemy.get_stat("age")}'
#                                          f'\nЗдоровье - {enemy.get_stat("hp")}'
#                                          f'\n#######'
#                                          f'\n{last_en_action}'
#                                          f'\n#########'
#                                          f'\nВаше здоровье - {db.return_user_info(call.message.chat.id)["hp"]}',
#                                          reply_markup=kb.battle_kb)
#         except aiogram.utils.exceptions.MessageNotModified:
#             await call.message.edit_text(f'Враг - {enemy.get_stat("name")}'
#                                          f'\nРаса - {enemy.get_stat("race")}'
#                                          f'\nРодом из - {enemy.get_stat("country")}'
#                                          f'\nВозраст - {enemy.get_stat("age")}'
#                                          f'\nЗдоровье - {enemy.get_stat("hp")}'
#                                          f'\n#######'
#                                          f'\n{"Ничего не изменилось"}'
#                                          f'\n#########'
#                                          f'\nВаше здоровье - {db.return_user_info(call.message.chat.id)["hp"]}',
#                                          reply_markup=kb.battle_kb)
#


async def change_frames(call, state):
    cb_data = call.data
    user = db.return_user_info(call.message.chat.id)
    now_frame = db.return_add_conditions_of_game(call.message.chat.id,user['game_code'])['frame_num']
    match cb_data:
        case cb_data.startswith('start_play_game'):
            await call.message.delete()
        case cb_data.startswith('frame_'):
            k = db.update_user_frame_num(call.message.chat.id, cb_data[6:], user['curr_game_code'])

async def change_frames_old(call,state):

        cb_data = call.data
        now_frame_num = db.return_user_info(call.message.chat.id)['frame_num']
        user = db.return_user_info(call.message.chat.id)
        k=0
        if cb_data == 'start_play_game':
            await call.message.delete()
        if cb_data.startswith('frame_'):
            k = db.update_user_frame_num(call.message.chat.id, cb_data[6:],user['curr_game_code'])
        elif cb_data.startswith('next_frame'):
            k = db.update_user_frame_num(call.message.chat.id,db.return_user_info(call.message.chat.id)['frame_num']+1,user['curr_game_code'])
        elif cb_data.startswith('start_play_game'):
            k = 1
        frame = db.return_frame(db.return_user_info(call.message.chat.id)['frame_num'])
        if frame != 0 and k != 0:
            match frame['modificators']:
                case 'battle':
                    if cb_data != 'start_play_game' and now_frame_num != int(cb_data[6:]):
                        # await start_battle(call,state)
                        pass

            if frame['content_code'] > 0:
                match frame['content_code']:
                    case 1:
                        content = InputMediaPhoto(media=frame['content'], caption=frame['desc'])
                    case 2:
                        content = InputMediaVideo(media=frame['content'],caption=frame['desc'])
                    case 3:
                        content = InputMediaAudio(media=frame['content'],caption=frame['desc'])
                    case _:
                        content = None

                markup = kb.read_kb
                if frame['is_variants']:
                    markup = InlineKeyboardMarkup()
                    j = frame['variants_frame'].split('\n')
                    for i in frame['variants'].split('\n'):
                        markup.add(InlineKeyboardButton(text=i, callback_data=f'frame_{j[0]}'))
                        j.pop(0)

                if db.return_user_info(call.message.chat.id)['state'] == 'free':
                    if frame['sticker'] != None:
                        await call.message.answer_sticker(frame['sticker'])
                    try:

                        await call.message.edit_media(content, reply_markup=markup)
                    except:
                        try:
                            await call.message.delete()
                        except:
                            pass
                        match frame['content_code']:
                            case 1:
                                await call.message.answer_photo(frame['content'], caption=frame['desc'], reply_markup=markup)
                            case 2:
                                await call.message.answer_video(frame['content'], caption=frame['desc'], reply_markup=markup)
                            case 3:
                                await call.message.answer_audio(frame['content'], caption=frame['desc'], reply_markup=markup)
                else:
                    try:
                        await call.message.delete()
                    except:
                        pass
                    if frame['modificators'] != 'battle':
                        await call.message.answer('Вы сейчас заняты другой активностью. Возвращайтесь, когда освободитесь')
            else:
                markup = kb.read_kb
                if frame['is_variants']:
                    markup = InlineKeyboardMarkup()
                    j = frame['variants_frame'].split('\n')
                    for i in frame['variants'].split('\n'):
                        markup.add(InlineKeyboardButton(text=i, callback_data=f'frame_{j[0]}'))
                        j.pop(0)
                if db.return_user_info(call.message.chat.id)['state'] == 'free':
                    if frame['sticker'] != None:
                        await call.message.answer_sticker(frame['sticker'])
                    try:
                        await call.message.edit_text(frame['desc'], reply_markup=markup)
                    except:
                        try:
                            await call.message.delete()
                        except:
                            pass
                        await call.message.answer(frame['desc'], reply_markup=markup)
                else:
                    try:
                        await call.message.delete()
                    except:
                        pass
                    if frame['modificators'] != 'battle':
                        await call.message.answer('Вы сейчас заняты другой активностью. Возвращайтесь, когда освободитесь')
        else:
            if db.return_user_info(call.message.chat.id)['state'] == 'free':
                try:
                    await call.message.delete()
                except:
                    pass
                await call.message.answer('На данном моменте сюжет кончается. Спасибо')
            else:
                try:
                    await call.message.delete()
                except:
                    pass
                if frame['modificators'] != 'battle':
                    await call.message.answer('Вы сейчас заняты другой активностью. Возвращайтесь, когда освободитесь')
            db.update_user_frame_num(call.message.chat.id, now_frame_num, user['curr_game_code'])

# @dp.callback_query_handler(lambda c: c.data)
# async def callback (call: types.CallbackQuery, state:FSMContext):
#     cb_data = call.data
#
#     # if cb_data.endswith('_battle'):
#     #     await continue_battle(call,state)
#
#     if cb_data.startswith('frame_'):
#         await change_frames(call,state)
#     if cb_data == 'start_play_game':
#         await change_frames(call,state)
#     if cb_data == 'next_frame':
#         await change_frames(call,state)


@dp.callback_query_handler(kb.show_more_game_genre.filter())
async def get_games_by_genre(call:types.CallbackQuery, callback_data: dict):

    markup = kb.return_library(db.return_game_by_genre(callback_data['genre_code'])).add(InlineKeyboardButton('Назад', callback_data=kb.store_action.new('go_to_genres')))
    await call.message.edit_text(f'Игры жанра {db.return_genre_name_by_code(callback_data["genre_code"])}:',reply_markup=markup)


@dp.callback_query_handler(kb.store_action.filter())
async def store_handler(call:types.CallbackQuery, callback_data: dict):
    if callback_data['action'] == 'go_to_genres':
        genres = db.return_genres()
        markup = kb.store_kb_genres(genres)
        await call.message.edit_text(f'Выберите интересующую вас категорию', reply_markup=markup)



@dp.callback_query_handler(kb.buy_game.filter())
async def buy_game(call:types.CallbackQuery, callback_data: dict):
    game_code = callback_data['game_code']
    game = db.return_game_info(game_code)
    match game['price']:
        case 0:
            db.give_game_to_user(game_code,call.message.chat.id, 0)
            await call.message.edit_text(f'{game["game_name"]} успешно добавлена в библиотеку')
        case _:
            pass


@dp.callback_query_handler(kb.show_more_info_game.filter())
async def show_game_info(call:types.CallbackQuery, callback_data: dict):
    game = db.return_game_info(callback_data['game_code'])
    await call.message.delete()
    media = types.MediaGroup()
    markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call.message.chat.id,game['game_code']), game['price'])
    if game['price'] > 0:
        game_info_text = f'{game["game_name"]}' \
                         f'\nИздатель - {game["publisher"]}' \
                         f'\nРазработчик - {game["creator"]}' \
                         f'\nЖанр - {game["genre"]}' \
                         f'\nОписание:' \
                         f'\n{game["game_description"]}' \
                         f'\nЦена - {game["price"]}'
    else:
        game_info_text = f'{game["game_name"]}' \
                         f'\nИздатель - {game["publisher"]}' \
                         f'\nРазработчик - {game["creator"]}' \
                         f'\nЖанр - {game["genre"]}' \
                         f'\nОписание:' \
                         f'\n{game["game_description"]}' \
                         f'\nЦена - Бесплатно'

    for index, file_id in enumerate(game['game_cover'].split('\n')):
        match index:
            case 0:
                match file_id.lower()[0]:
                    case 'b':
                        media.attach_video(video=file_id)
                    case 'a':
                        media.attach_photo(photo=file_id)
            case _:
                match file_id.lower()[0]:
                    case 'b':
                        media.attach_video(video=file_id)
                    case 'a':
                        media.attach_photo(photo=file_id)
    await call.message.answer_media_group(media)
    await call.message.answer(game_info_text, reply_markup=markup)



async def on_startup(_):
    print('Бот вышел в онлайн')
if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)




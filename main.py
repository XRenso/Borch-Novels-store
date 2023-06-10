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

import enemy_generator
from database import Mongo as mg
import keyboards as kb
from dotenv import load_dotenv
import os
import logging

storage=MemoryStorage()
load_dotenv()
bot = Bot(token = os.getenv('TOKEN'))
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot=bot,storage=storage)


db = mg()
db.__init__()




class Cache(StatesGroup):
    enemy = State()
    frame = State()




@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    db.add_user(message.from_user.id)
    # await message.answer('MVP показ возможностей для телеграм игры. \nСмерть, продажа, покупка, воскрешение', reply_markup=kb.start_game)
    await message.answer(f'Здравствуй, {message.from_user.first_name}!'
                            f'\nДобро пожаловать в магазин Borch Novels.')
@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    id_photo = message.photo[-1].file_id
    await message.answer_photo(id_photo,caption=id_photo)
@dp.message_handler(content_types=['video'])
async def handle_photo(message: types.Message):
    id_video = message.video.file_id
    await message.answer_video(id_video,caption=id_video)
@dp.message_handler(content_types=['sticker'])
async def handle_photo(message: types.Message):
    id_sticker = message.sticker.file_id
    await message.answer_sticker(id_sticker)
    await message.answer(id_sticker)
@dp.message_handler(content_types=['audio'])
async def handle_photo(message: types.Message):
    id_audio = message.audio.file_id
    await message.answer_audio(id_audio,caption=id_audio)


@dp.message_handler(commands=['reset'])
async def reset(message:types.Message):
    db.update_user_frame_num(message.from_user.id, 1)
    await message.answer('Успешно сброшено')

async def start_battle(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if call.data.startswith('frame') or call.data.endswith('frame'):
        await state.update_data(frame=call)
    if data.get('enemy') == None:
        async with state.proxy():
            enemy = enemy_generator.create_monster()
            await state.update_data(enemy=enemy)
            data = await state.get_data()
    enemy = data.get('enemy')
    last_action = 'Ничего не произошло'
    await call.message.answer(f'Враг - {enemy.get_stat("name")}'
                         f'\nРаса - {enemy.get_stat("race")}'
                         f'\nРодом из - {enemy.get_stat("country")}'
                         f'\nВозраст - {enemy.get_stat("age")}'
                         f'\nЗдоровье - {enemy.get_stat("hp")}'
                         f'\n#######'
                         f'\n{last_action}'
                         f'\n#########'
                         f'\nВаше здоровье - {db.return_user_info(call.message.chat.id)["hp"]}',reply_markup=kb.battle_kb)
    db.change_user_state(call.message.chat.id,1)

async def continue_battle(call, state):
    cb_data = call.data
    data = await state.get_data()
    enemy = data.get('enemy')
    enemy_move = random.randrange(2)
    last_en_action = 'Ничего не произошло'
    if cb_data.startswith('punch'):
        user_dmg = db.return_user_info(call.message.chat.id)['dmg']
        enemy.get_damage(random.randrange(user_dmg // 2, user_dmg + 1))
    elif cb_data.startswith('heal'):
        db.user_health(call.message.chat.id, random.randrange(1, db.return_user_info(call.message.chat.id)['hp']))
    match enemy_move:
        case 1:
            last_en_action = db.user_get_dmg(call.message.chat.id, enemy.attack())
        case 0:
            last_en_action = enemy.health()
    await state.update_data(enemy=enemy)
    if db.return_user_info(call.message.chat.id)['hp'] == 0 and not enemy.dead():
        await call.message.answer_sticker('CAACAgEAAxkBAAIDimR_1TToDteE_e_htszvUey4rLOgAAIHAAPJd9FOnQpx5SSzvvQvBA')
        await call.message.edit_text('Вы погибли. Земля водой')
        await state.reset_state()
        db.change_user_state(call.message.chat.id,0)
    elif enemy.dead() and db.return_user_info(call.message.chat.id)['hp'] == 0:
        await call.message.answer_sticker('CAACAgEAAxkBAAIDimR_1TToDteE_e_htszvUey4rLOgAAIHAAPJd9FOnQpx5SSzvvQvBA')
        await call.message.edit_text('Вы оба погибли. Водичка')
        await state.reset_state()
        db.change_user_state(call.message.chat.id,0)
    elif enemy.dead() and db.return_user_info(call.message.chat.id)['hp'] != 0:
        await call.message.edit_text('Вы победили. Сыр маслом')
        await state.reset_state()
        db.change_user_state(call.message.chat.id, 0)
        await change_frames(data.get('frame'), state)

    else:
        try:
            await call.message.edit_text(f'Враг - {enemy.get_stat("name")}'
                                         f'\nРаса - {enemy.get_stat("race")}'
                                         f'\nРодом из - {enemy.get_stat("country")}'
                                         f'\nВозраст - {enemy.get_stat("age")}'
                                         f'\nЗдоровье - {enemy.get_stat("hp")}'
                                         f'\n#######'
                                         f'\n{last_en_action}'
                                         f'\n#########'
                                         f'\nВаше здоровье - {db.return_user_info(call.message.chat.id)["hp"]}',
                                         reply_markup=kb.battle_kb)
        except aiogram.utils.exceptions.MessageNotModified:
            await call.message.edit_text(f'Враг - {enemy.get_stat("name")}'
                                         f'\nРаса - {enemy.get_stat("race")}'
                                         f'\nРодом из - {enemy.get_stat("country")}'
                                         f'\nВозраст - {enemy.get_stat("age")}'
                                         f'\nЗдоровье - {enemy.get_stat("hp")}'
                                         f'\n#######'
                                         f'\n{"Ничего не изменилось"}'
                                         f'\n#########'
                                         f'\nВаше здоровье - {db.return_user_info(call.message.chat.id)["hp"]}',
                                         reply_markup=kb.battle_kb)



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
        k=0
        if cb_data == 'start_play_game':
            await call.message.delete()
        if cb_data.startswith('frame_'):
            k = db.update_user_frame_num(call.message.chat.id, cb_data[6:])
        elif cb_data.startswith('next_frame'):
            k = db.update_user_frame_num(call.message.chat.id,db.return_user_info(call.message.chat.id)['frame_num']+1)
        elif cb_data.startswith('start_play_game'):
            k = 1
        frame = db.return_frame(db.return_user_info(call.message.chat.id)['frame_num'])
        if frame != 0 and k != 0:
            match frame['modificators']:
                case 'battle':
                    if cb_data != 'start_play_game' and now_frame_num != int(cb_data[6:]):
                        await start_battle(call,state)

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
            db.update_user_frame_num(call.message.chat.id, now_frame_num)

@dp.callback_query_handler(lambda c: c.data)
async def callback (call: types.CallbackQuery, state:FSMContext):
    cb_data = call.data

    if cb_data.endswith('_battle'):
        await continue_battle(call,state)

    if cb_data.startswith('frame_'):
        await change_frames(call,state)
    if cb_data == 'start_play_game':
        await change_frames(call,state)
    if cb_data == 'next_frame':
        await change_frames(call,state)



async def on_startup(_):
    print('Бот вышел в онлайн')
if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)




import aiogram.utils.exceptions
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, \
    LabeledPrice, PreCheckoutQuery
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

class Cache(StatesGroup):
    sound = State()
    game_text = State()
    achivement = State()

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


@dp.message_handler(commands = ['reset_now_game'])
async def reset_cur_game(message:types.Message):
    user = db.return_user_info(message.from_user.id)
    db.reset_game_setings(user_id=message.from_user.id,game_code=user['curr_game_code'])
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
            if user_info != 0:
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
            else:
                await message.answer('Пройдите регистрацию. Отправив сообщение /start')


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


@dp.callback_query_handler(kb.show_more_game_genre.filter())
async def get_games_by_genre(call:types.CallbackQuery, callback_data: dict):

    markup = kb.return_library(db.return_game_by_genre(callback_data['genre_code'])).add(InlineKeyboardButton('Назад', callback_data=kb.store_action.new('go_to_genres')))
    await call.message.edit_text(f'Игры жанра {db.return_genre_name_by_code(callback_data["genre_code"])}:',reply_markup=markup)



@dp.callback_query_handler(kb.frame_change.filter())
async def change_frames(call:types.CallbackQuery, callback_data: dict, state:FSMContext):
    user = db.return_user_info(call.message.chat.id)
    game = db.return_game_info(user['curr_game_code'])
    game_cfg = db.return_game_cfg(user['user_id'], game['game_code'])
    data = await state.get_data()
    frame_num = int(callback_data['frame_num'])
    frame = db.return_frame(frame_num=frame_num,game_code=game['game_code'])

    if data.get('achivement') is not None:
        try:
            await call.bot.delete_message(message_id=data.get('achivement').message_id,chat_id=call.message.chat.id)
        except:
            pass
    if data.get('game_text') is not None and data.get('game_text').message_id != call.message.message_id:
        try:
            await call.message.edit_text('Сессия устарела\nЗапустите игру заново')
        except:
            await call.message.delete()
            await call.message.answer('Сессия устарела \nЗапустите игру заново.')
    else:
        if frame != 0:
            if game_cfg['is_demo'] <= frame['is_demo']:
                db.update_user_frame_num(user['user_id'], frame_num, game['game_code'])
                match frame['content_code']:
                    case 1:
                        content = InputMediaPhoto(media=frame['content'], caption=frame['text']['ru'])
                    case 2:
                        content = InputMediaVideo(media=frame['content'], caption=frame['text']['ru'])
                    case 3:
                        content = InputMediaAudio(media=frame['content'], caption=frame['text']['ru'])
                    case _:
                        content = None

                markup = InlineKeyboardMarkup()
                frame_num = list(frame['variants_frame'].split('\n'))
                for i in frame['variants'].split('\n'):
                    markup.add(InlineKeyboardButton(i, callback_data=kb.frame_change.new(frame_num[0])))
                    frame_num.pop(0)
                try:
                    await call.message.edit_media(content, reply_markup=markup)
                except:
                    try:
                        await call.message.delete()
                    except:
                        pass
                    async with state.proxy():
                        match frame['content_code']:
                            case 1:
                               message = await call.message.answer_photo(frame['content'], caption=frame['text']['ru'], reply_markup=markup)
                            case 2:
                                message = await call.message.answer_video(frame['content'], caption=frame['text']['ru'], reply_markup=markup)
                            case 3:
                                message = await call.message.answer_audio(frame['content'], caption=frame['text']['ru'], reply_markup=markup)
                            case _:
                                message = await call.message.answer(frame['text']['ru'], reply_markup=markup)
                        await state.update_data(game_text=message)
            else:
                await call.message.delete()
                await call.message.answer('На этом демо игры заканчивается. Приобретите полную версию игры')
            if frame['sound']:
                if data.get('sound') == None:
                    async with state.proxy():
                        sound = await call.message.answer_audio(frame['sound'])
                        await state.update_data(sound=sound)
                else:
                    await call.bot.delete_message(message_id=data.get('sound').message_id, chat_id=call.message.chat.id)
                    async with state.proxy():
                        sound = await call.message.answer_audio(frame['sound'])
                        await state.update_data(sound=sound)

            if frame['achivement']:
                achiv = db.give_achivement_to_user(game_code=game['game_code'],achivement_code=frame['achivement'], user_id=call.message.chat.id)
                if achiv != 0:
                    async with state.proxy():
                        achivement = db.return_achivement(game_code=game['game_code'], achivement_code=frame['achivement'])
                        ok = await call.message.answer(text=f'Получено достижение {achivement["name"]}\nЧтобы посмотреть все достижения перейдите к меню достижений')
                        await state.update_data(achivement=ok)


        else:


           try:
                await call.message.edit_text('На этом игра заканчивается благодарим за прохождение')
           except:
               await call.message.delete()
               await call.message.answer('На этом игра заканчивается. Благодарим за прохождение')


@dp.callback_query_handler(kb.get_demo.filter())
async def get_demo_to_user(call:types.CallbackQuery, callback_data: dict, state:FSMContext):
    db.give_game_to_user(user_id=call.message.chat.id, game_code=callback_data['game_code'], is_demo=1)
    await call.message.edit_text(f'Успешно полученая демо-версия игры - {db.return_game_info(callback_data["game_code"])["game_name"]}')

@dp.callback_query_handler(kb.play_game.filter())
async def start_play(call:types.CallbackQuery, callback_data: dict, state:FSMContext):
    game = db.return_game_info(callback_data['game_code'])
    game_user_cfg = db.return_game_cfg(call.message.chat.id,game['game_code'])
    frame = db.return_frame(game_code=game['game_code'],frame_num=game_user_cfg['frame_num'])
    data = await state.get_data()
    await call.message.delete()
    if frame != 0:
        if data.get('game_text'):
            try:
                await call.bot.delete_message(chat_id=call.message.chat.id,message_id=data.get('game_text').message_id)
            except aiogram.utils.exceptions.MessageToDeleteNotFound:
                pass
        db.update_now_user_game(call.message.chat.id,game['game_code'])

        match frame['content_code']:
            case 1:
                content = InputMediaPhoto(media=frame['content'], caption=frame['text']['ru'])
            case 2:
                content = InputMediaVideo(media=frame['content'], caption=frame['text']['ru'])
            case 3:
                content = InputMediaAudio(media=frame['content'], caption=frame['text']['ru'])
            case _:
                content = None

        markup = InlineKeyboardMarkup()
        frame_num = list(frame['variants_frame'].split('\n'))
        for i in frame['variants'].split('\n'):
            markup.add(InlineKeyboardButton(i, callback_data=kb.frame_change.new(frame_num[0])))
            frame_num.pop(0)
        try:
            await call.message.edit_media(content, reply_markup=markup)
        except:
            try:
                await call.message.delete()
            except:
                pass
            async with state.proxy():
                match frame['content_code']:
                    case 1:
                        message = await call.message.answer_photo(frame['content'], caption=frame['text']['ru'], reply_markup=markup)
                    case 2:
                        message = await call.message.answer_video(frame['content'], caption=frame['text']['ru'],reply_markup=markup)
                    case 3:
                        message = await call.message.answer_audio(frame['content'], caption=frame['text']['ru'],reply_markup=markup)
                    case _:
                        message = await call.message.answer(frame['text']['ru'],reply_markup=markup)
                await state.update_data(game_text=message)
        if frame['sound']:
            if data.get('sound') == None:
                async with state.proxy():
                    sound = await call.message.answer_audio(frame['sound'])
                    await state.update_data(sound=sound)
            else:
                await call.bot.delete_message(message_id=data.get('sound').message_id, chat_id=call.message.chat.id)
                async with state.proxy():
                    sound = await call.message.answer_audio(frame['sound'])

                    await state.update_data(sound=sound)
    else:
        await call.message.answer('У игры пока нет кадров. Но скоро это будет исправлено')



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
            await call.message.delete()
            await call.bot.send_invoice(
                chat_id=call.message.chat.id,
                title= f'Покупка игры {game["game_name"]}',
                description=game['game_description'],
                payload=f'{game["game_code"]}',
                provider_token='381764678:TEST:59097',
                currency='rub',
                prices=[
                    LabeledPrice(
                        label='Доступ к игре',
                        amount=game['price']*100
                    ),
                    LabeledPrice(
                        label='Скидка',
                        amount=-game['discount'] * 100
                    )
                ],
                max_tip_amount=150*100,
                suggested_tip_amounts=[10*100,50*100,100*100,150*100],
                start_parameter='no',
                provider_data=None,
                # photo_url=game['game_cover'].split('\n')[0],
                # photo_size=100,
                # photo_width=800,
                # photo_height=450,
                need_name=False,
                need_email=False,
                need_phone_number=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False,
                disable_notification=False,
                protect_content=False,
                reply_to_message_id=False,
                allow_sending_without_reply=True,
                reply_markup=None,

            )



@dp.pre_checkout_query_handler()
async def give_paid_game_to_user(pre_checkout_query:PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id,ok=True)


@dp.message_handler(content_types=['successful_payment'])
async def uspeh_buy(message:types.Message):
    game = db.return_game_info(message.successful_payment.invoice_payload)
    db.give_game_to_user(game['game_code'], message.from_user.id, 0)
    await message.answer(f'Благодарим вас за покупку на сумму {message.successful_payment.total_amount//100} руб.'
                         f'\n Игра - {game["game_name"]}  - успешно добавлена в вашу библиотеку')

@dp.callback_query_handler(kb.unavailable_game.filter())
async def unavailable_game(call:types.CallbackQuery, callback_data: dict):
    game = db.return_game_info(callback_data['game_code'])
    await call.message.edit_text(f'Мы понимаем как вы хотите поиграть в {game["game_name"]}'
                                 f'\nОднако сейчас игра недоступна. Наши сожаления'
                                 f'\nПодождите официального выхода')


@dp.callback_query_handler(kb.show_more_info_game.filter())
async def show_game_info(call:types.CallbackQuery, callback_data: dict):
    game = db.return_game_info(callback_data['game_code'])
    await call.message.delete()
    media = types.MediaGroup()
    markup = kb.get_game(game['game_code'], db.check_is_game_in_user_library(call.message.chat.id,game['game_code']), game['price'], user_id=call.message.chat.id)
    if game['price'] > 0:
        game_info_text = f'{game["game_name"]}' \
                         f'\nИздатель - {game["publisher"]}' \
                         f'\nРазработчик - {game["creator"]}' \
                         f'\nЖанр - {game["genre"]}' \
                         f'\nОписание:' \
                         f'\n{game["game_description"]}' \
                         f'\nЦена - {game["price"]} руб'
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




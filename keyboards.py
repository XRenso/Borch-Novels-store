from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
import phrase as phr
from database import Mongo as mg
db = mg()
db.__init__()
#Callback data preset
frame_change = CallbackData('frame','frame_num')
play_game = CallbackData('playing_game', 'game_code')

show_by_genre = CallbackData('gen', 'genre_code')
show_more_info_game = CallbackData('game', 'game_code')
show_more_game_genre = CallbackData('genre','genre_code')

buy_game = CallbackData('game_buying', 'game_code')
get_demo = CallbackData('demo_game', 'game_code')


store_action = CallbackData('store', 'action')




vpered = InlineKeyboardMarkup(row_width=1)
vpered.add(InlineKeyboardButton(text='️Продолжить повествование ▶️',callback_data='vpered'))

nachat_start = InlineKeyboardMarkup(row_width=1)
nachat_start.add(InlineKeyboardButton(text='Начать игру  ▶️',callback_data='nachat'))




start_btn = InlineKeyboardButton('Начать', callback_data='start_play_game')
start_game = InlineKeyboardMarkup().add(start_btn)

next_btn = InlineKeyboardButton('➤', callback_data='next_frame')
read_kb = InlineKeyboardMarkup().add(next_btn)


##batle
fight_btn = InlineKeyboardButton('Бить', callback_data='punch_battle')
heal_btn = InlineKeyboardButton('Лечиться', callback_data='heal_battle')
battle_kb = InlineKeyboardMarkup().add(fight_btn,heal_btn)

##Main kb
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
about_me = KeyboardButton(phr.profile)
library = KeyboardButton(phr.library)
shop = KeyboardButton(phr.shop)
main_kb.add(shop).row(library,about_me)

##Shop kb
store = KeyboardButton(phr.store)
find_game = KeyboardButton(phr.search_game)
main_menu = KeyboardButton(phr.main_menu)
shop_kb = ReplyKeyboardMarkup(resize_keyboard=True)
shop_kb.add(store,find_game).add(main_menu)

def return_library(games):
    markup = InlineKeyboardMarkup()
    for i in games:
        markup.add(InlineKeyboardButton(i['game_name'], callback_data=show_more_info_game.new(i['game_code'])))
    return markup

def store_kb_genres(genre):
    markup = InlineKeyboardMarkup()
    for i in genre:
        markup.add(InlineKeyboardButton(db.return_genre_name_by_code(i),callback_data=show_more_game_genre.new(i)))
    return markup

def get_game(game_code:str, have_it_user:int, price:int) -> InlineKeyboardMarkup:
    match have_it_user:
        case 1:
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton('Играть', callback_data=play_game.new(game_code)))
        case _:
            markup = InlineKeyboardMarkup()
            match price:
                case 0:
                    markup.add(InlineKeyboardButton('Получить', callback_data=buy_game.new(game_code)))
                case _:
                    markup.add(InlineKeyboardButton('Купить', callback_data=buy_game.new(game_code)))
                    markup.add(InlineKeyboardButton('Получить демо', callback_data=get_demo.new(game_code)))

    return markup
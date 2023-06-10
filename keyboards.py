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
show_by_genre = CallbackData('gen', 'genre_code')
show_more_info_game = CallbackData('game', 'game_code')
show_more_game_genre = CallbackData('genre','genre_code')
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
find_game = KeyboardButton(phr.search_game)
store = KeyboardButton(phr.store)
main_kb.add(store,find_game).row(library,about_me)


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
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types

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
about_me = KeyboardButton('Профиль')
library = KeyboardButton('Библиотека игр')
find_game = KeyboardButton('Найти игру')
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

unavailable_game = CallbackData('unavailable', 'game_code')

store_action = CallbackData('store', 'action')


profile_achivement_games = CallbackData('games', 'game_code')
profile_achivement_code = CallbackData('achivements','achivement_code')
profile_action = CallbackData('profile', 'action')



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

##Shop kz
store = KeyboardButton(phr.store)
find_game = KeyboardButton(phr.search_game)
main_menu = KeyboardButton(phr.main_menu)
shop_kb = ReplyKeyboardMarkup(resize_keyboard=True)
shop_kb.add(store,find_game).add(main_menu)




##profile keyboard
back_to_profile = InlineKeyboardButton('Назад ↩️', callback_data=profile_action.new('back_to_profile'))
back_to_games = InlineKeyboardButton('Назад ↩️',callback_data=profile_action.new('back_to_games'))
show_achivements = InlineKeyboardButton('Показать достижения ✅ ', callback_data=profile_action.new('show_achivements'))
bad_achivements = InlineKeyboardButton('У вас нет достижений ❌', callback_data=profile_action.new('no_achivements'))

profile_kb_have_achivements = InlineKeyboardMarkup().add(show_achivements)

profile_kb_not_have_achivements = InlineKeyboardMarkup().add(bad_achivements)



def return_games_btn_achivement(games):
    if games != 0:
        markup = InlineKeyboardMarkup()
        for i in games:
            game = db.return_game_info(i)
            markup.add(InlineKeyboardButton(game['game_name'], callback_data=profile_achivement_games.new(i)))
        return markup


def return_achivements(achivments,game_code):
    markup = InlineKeyboardMarkup()
    for i in achivments:
        achivment = db.return_achivement(game_code=game_code, achivement_code=i)
        if achivment != 0:
            markup.add(InlineKeyboardButton(achivment["name"], callback_data=profile_achivement_code.new(f"{game_code}<@{achivment['achivement_code']}")))
    return markup


def return_library(games):
    markup = InlineKeyboardMarkup()
    if games != 0:
        for i in games:
            markup.add(InlineKeyboardButton(i['game_name'], callback_data=show_more_info_game.new(i['game_code'])))
    return markup

def store_kb_genres(genre):
    markup = InlineKeyboardMarkup()
    for i in genre:
        markup.add(InlineKeyboardButton(db.return_genre_name_by_code(i),callback_data=show_more_game_genre.new(i)))
    return markup

def get_game(game_code:str, have_it_user:int, price:int, user_id:int) -> InlineKeyboardMarkup:
    check_frame = db.return_frame(1,game_code)
    game = db.return_game_info(game_code)
    markup = InlineKeyboardMarkup()
    game_cfg = db.return_game_cfg(user_id, game_code)
    if check_frame != 0 and game['can_buy'] != 0:
        match have_it_user:
            case 1 if not game_cfg or game_cfg['is_demo'] == 0:
                markup.add(InlineKeyboardButton('Играть 🎮', callback_data=play_game.new(game_code)))
            case _:
                match price:
                    case 0:
                        markup.add(InlineKeyboardButton('Получить 👇', callback_data=buy_game.new(game_code)))
                    case _:
                            if game_cfg == 0:
                                markup.add(InlineKeyboardButton('Купить 💳', callback_data=buy_game.new(game_code)))
                            elif game_cfg['is_demo'] == 1:
                                markup.add(InlineKeyboardButton('Купить полную версию игры 💳', callback_data=buy_game.new(game_code)))
                            if game_cfg == 0:
                                markup.add(InlineKeyboardButton('Получить демо 👇', callback_data=get_demo.new(game_code)))
                            else:
                                    markup.add(InlineKeyboardButton('Играть 🎮', callback_data=play_game.new(game_code)))
    else:
        if have_it_user == 0:
            markup.add(InlineKeyboardButton('Игра недоступна ❌', callback_data=unavailable_game.new(game_code)))
        else:
            markup.add(InlineKeyboardButton('Играть 🎮', callback_data=play_game.new(game_code)))
    return markup

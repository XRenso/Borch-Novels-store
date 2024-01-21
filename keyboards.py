from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
import phrase as phr
from database import Mongo as mg
db = mg()
db.__init__()
#Callback data preset
admin_frame_info = CallbackData('admin','frame_num','game_code')


send_everyone = CallbackData('rssA', 'confirm')

frame_change = CallbackData('frame','frame_num')
play_game = CallbackData('playing_game', 'game_code')
rate_game = CallbackData('rate', 'game_code')
rating = CallbackData('rating_score','score')

show_by_genre = CallbackData('gen', 'genre_code')
show_more_info_game = CallbackData('game', 'game_code')
show_more_game_genre = CallbackData('genre','type_code','genre_code', 'page')
show_genres_by_type = CallbackData('type', 'type_code')
inline_show_game_info = CallbackData('inline_game','game_code')
get_game_info = CallbackData('info_game', 'game_code')
buy_game = CallbackData('game_buying', 'game_code')
get_demo = CallbackData('demo_game', 'game_code')

get_all_pages = CallbackData('pages', 'type','type_code','category_code')
end_list = CallbackData('pgs_end','info')


next_page = CallbackData('change_page','category')

donate = CallbackData('donate','thx')

unavailable_game = CallbackData('unavailable', 'game_code')

store_action = CallbackData('store', 'action')

delete_game_from_library = CallbackData('delete_game','game_code')

game_statistic = CallbackData('analytic', 'game_code')

profile_achivement_games = CallbackData('games', 'game_code')
profile_achivement_code = CallbackData('achivements','achivement_code')
profile_action = CallbackData('profile', 'action')


change_page_manual = CallbackData('changing_page','info')

paper_cb = CallbackData('paper', 'agree')


reset_games_cb = CallbackData('res_games','game_code')
confirm_reset_cb = CallbackData('conf_res','game_code')
cancel_reset_cb = CallbackData('canc_res','ok')
back_reset_cb = CallbackData('back_to_res','ok')

back_to_types_from_genre = CallbackData('back_to_types','ok')

start_btn = InlineKeyboardButton('Начать', callback_data='start_play_game')
start_game = InlineKeyboardMarkup().add(start_btn)


get_user_group = CallbackData('user_group','group_name', 'page')
back_to_user_group = CallbackData('back_to_user_groups','back')
add_to_user_group = CallbackData('add_to_user_group','game_code')
remove_from_user_group = CallbackData('remove_from_user_group','game_code')
control_user_group = CallbackData('control_user_group', 'game_code')
choose_group_add = CallbackData('g_a','game_code', 'group_name')
choose_group_remove = CallbackData('g_r', 'game_code','group_name')
create_new_user_group = CallbackData('create_user_group','game_code')

get_user_group_for_reset = CallbackData('gugfr','group_name')

##Agreement
paper = InlineKeyboardButton('Пользовательское соглашение', url='https://telegra.ph/Polzovatelskoe-soglashenie-06-21-6')
agree = InlineKeyboardButton('Принять ✅', callback_data=paper_cb.new('ye'))

agreement_ikb = InlineKeyboardMarkup().add(paper).add(agree)

##Main kb
main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
about_me = KeyboardButton(phr.profile)
library = KeyboardButton(phr.library)
shop = KeyboardButton(phr.shop)
about_us = KeyboardButton(phr.about_us)
main_kb.row(library,shop).row(about_us,about_me)

##Shop kb
store = KeyboardButton(phr.store)
find_game = KeyboardButton(phr.search_game)
shop_statistic = KeyboardButton(phr.shop_statistic)
main_menu = KeyboardButton(phr.main_menu)
shop_kb = ReplyKeyboardMarkup(resize_keyboard=True)
shop_kb.add(store,find_game).row(shop_statistic,main_menu)




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


def return_library(games, type='lib',page=0, category_code=None, type_code=None):
    markup = InlineKeyboardMarkup()
    if len(games) <= 5:
        if games != 0:
            for i in games:
                markup.add(InlineKeyboardButton(i['game_name'], callback_data=show_more_info_game.new(i['game_code'])))
    else:
        counter = len(games)//5
        if len(games)%5 !=0:
            counter+=1
        games = games[5*page:5*page+5]
        for i in games:
            markup.add(InlineKeyboardButton(i['game_name'], callback_data=show_more_info_game.new(i['game_code'])))
        match type:
            case 'store':
                page_counter = InlineKeyboardButton(f'{page + 1}/{counter}',
                                                    callback_data=get_all_pages.new(type, type_code, category_code))

                if page > 0:
                    back_btn = InlineKeyboardButton('⬅️', callback_data=show_more_game_genre.new(type_code,category_code,str(page-1)))
                else:
                    back_btn = InlineKeyboardButton('⬅️', callback_data=end_list.new('bad'))

                if 5*(page+1) in range(len(games)+1):
                    next_btn = InlineKeyboardButton('➡️', callback_data=show_more_game_genre.new(type_code,category_code,str(page+1)))
                else:
                    next_btn = InlineKeyboardButton('➡️', callback_data=end_list.new('bad'))

                markup.add(back_btn,
                           page_counter,
                           next_btn)
            case 'lib':
                page_counter = InlineKeyboardButton(f'{page + 1}/{counter}',
                                                    callback_data=get_all_pages.new(type, 'n', category_code))

                if page > 0:
                    back_btn = InlineKeyboardButton('⬅️',
                                                    callback_data=get_user_group.new(category_code, str(page - 1)))
                else:
                    back_btn = InlineKeyboardButton('⬅️',
                                                    callback_data=end_list.new('bad'))

                if 5 * (page + 1) in range(len(games)+1):
                    next_btn = InlineKeyboardButton('➡️', callback_data=
                        get_user_group.new(category_code, str(page + 1)))
                else:
                    next_btn = InlineKeyboardButton('➡️', callback_data=
                        end_list.new('bad'))

                markup.add(back_btn,
                           page_counter,
                           next_btn)
    return markup

def lib_category(categories):
    markup = InlineKeyboardMarkup()
    for key,_ in categories.items():
        markup.add(InlineKeyboardButton(key, callback_data=get_user_group.new(key, '0')))
    return markup
def reset_library(games):
    markup = InlineKeyboardMarkup()
    if games !=0 :
        for i in games:
            markup.add(InlineKeyboardButton(i['game_name'], callback_data=reset_games_cb.new(i['game_code'])))
    return markup
def reset_library_categories(categories):
    markup = InlineKeyboardMarkup()
    if categories != 0 :
        for key, _ in categories.items():
            markup.add(InlineKeyboardButton(key, callback_data=get_user_group_for_reset.new(key)))
    return markup

def store_kb_genres(genre, type_code):
    markup = InlineKeyboardMarkup(row_width=1)
    for i in genre:
        markup.insert(InlineKeyboardButton(db.return_genre_name_by_code(i, type_code=type_code),callback_data=show_more_game_genre.new(type_code,i,'0')))

    return markup

def store_kb_types(type):
    markup = InlineKeyboardMarkup(row_width=1)
    for i in type:
        markup.insert(InlineKeyboardButton(db.return_type_name_by_code(i),callback_data=show_genres_by_type.new(i)))
    return markup
def get_game(game_code:str, have_it_user:int, price:int, user_id:int) -> InlineKeyboardMarkup:
    check_frame = db.return_frame(1,game_code)
    game = db.return_game_info(game_code)
    markup = InlineKeyboardMarkup()
    game_cfg = db.return_game_cfg(user_id, game_code)
    user = db.return_user_info(user_id)
    if check_frame != 0 and game['can_buy'] != 0:
        match have_it_user:
            case 1 if not game_cfg or game_cfg['is_demo'] == 0:
                markup.row(InlineKeyboardButton('Запустить 🎮', callback_data=play_game.new(game_code)), InlineKeyboardButton('Оценить 🌟', callback_data=rate_game.new(game_code)))
            case _:
                match price:
                    case 0:
                        markup.add(InlineKeyboardButton('Получить 👇', callback_data=buy_game.new(game_code)))
                    case _:
                            if game_cfg == 0:
                                markup.add(InlineKeyboardButton('Купить 💳', callback_data=buy_game.new(game_code)))
                            elif game_cfg['is_demo'] == 1:
                                markup.add(InlineKeyboardButton('Купить полную версию 💳', callback_data=buy_game.new(game_code)))
                            if game_cfg == 0:
                                markup.add(InlineKeyboardButton('Получить демо 👇', callback_data=get_demo.new(game_code)))
                            else:
                                    markup.add(InlineKeyboardButton('Запустить 🎮', callback_data=play_game.new(game_code)))
    else:
        if have_it_user == 0:
            markup.add(InlineKeyboardButton('Продукт недоступен ❌', callback_data=unavailable_game.new(game_code)))
        else:
            markup.row(InlineKeyboardButton('Запустить 🎮', callback_data=play_game.new(game_code)), InlineKeyboardButton('Оценить 🌟', callback_data=rate_game.new(game_code)))

    if user['is_admin'] == 1:
        markup.add(InlineKeyboardButton(phr.statistic,callback_data=game_statistic.new(game_code)))

    if have_it_user == 1:
        markup.add(InlineKeyboardButton(phr.control_user_group, callback_data=control_user_group.new(game_code)))

    elif db.get_user_group_by_game(user_id, game_code, 0):
        markup.add(InlineKeyboardButton(phr.remove_from_user_group, callback_data=remove_from_user_group.new(game_code)))

    if price == 0 and have_it_user == 1:
        markup.add(InlineKeyboardButton(phr.delete_game_from_lib, callback_data=delete_game_from_library.new(game_code)))
    return markup.add(InlineKeyboardButton(text=phr.share_game, switch_inline_query=game['game_name']))

from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, InlineKeyboardMarkup
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardButton, KeyboardButton)
from aiogram.filters.callback_data import CallbackData
import phrase as phr
from database import Mongo as mg
db = mg()
db.__init__()
#Callback data preset
class Admin_CallbackData(CallbackData,prefix='admin'):
    frame_num: int
    game_code: str

class RSS_CallbackData(CallbackData,prefix='rssA'):
    confirm: str

class FrameChange_CallbackData(CallbackData,prefix='frame_num'):
    frame_num:int


class PlayingGame_CallbackData(CallbackData,prefix='playing_game'):
    game_code:str

class RateGame_CallbackData(CallbackData,prefix='rate'):
    game_code:str

class Rating_CallbackData(CallbackData,prefix='rating_score'):
    game_code:str
    score:int

class ShowByGenre_CallbackData(CallbackData,prefix='gen'):
    genre_code:str

class ShowMoreInfoGame_CallbackData(CallbackData,prefix='game'):
    game_code:str

class ShowMoreGameGenre_CallbackData(CallbackData,prefix='genre'):
    type_code:str
    genre_code:str
    page:int

class ShowGenresByType_CallbackData(CallbackData,prefix='type'):
    type_code:str

class InlineShowGameInfo_CallbackData(CallbackData,prefix='inline_game'):
    game_code:str

class GetGameInfo_CallbackData(CallbackData,prefix='info_game'):
    game_code:str


class BuyGame_CallbackData(CallbackData,prefix='game_buying'):
    game_code:str

class GetDemo_CallbackData(CallbackData,prefix='demo_game'):
    game_code:str

class GetAllPages_CallbackData(CallbackData,prefix='pages'):
    type:str
    type_code:str
    category_code:str

class EndList_CallbackData(CallbackData,prefix='pgs_end'):
    info:str

class NextPage_CallbackData(CallbackData, prefix='change_page'):
    category:str

class Donate_CallbackData(CallbackData, prefix='donate'):
    thx:str


class UnavailableGame_CallbackData(CallbackData, prefix='unavailable'):
    game_code:str

class StoreAction_CallbackData(CallbackData, prefix='store'):
    action:str
    type_code:str


class DeleteGameFromLibrary_CallbackData(CallbackData,prefix='delete_game'):
    game_code:str

class GameStatistic_CallbackData(CallbackData, prefix='analytic'):
    game_code:str

class ProfileAchivementGames_CallbackData(CallbackData, prefix='games'):
    game_code:str

class ProfileAchivementCode_CallbackData(CallbackData, prefix='achivements'):
    game_code:str
    achivement_code:str


class ProfileAction_CallbackData(CallbackData, prefix='profile'):
    action:str

class ChangePageManual_CallbackData(CallbackData, prefix='changing_page'):
    game_code:str



class PaperAgree_CallbackData(CallbackData, prefix='paper'):
    agree:str

class ResetGame_CallbackData(CallbackData, prefix='res_games'):
    game_code:str

class ConfirmResetGame_CallbackData(CallbackData, prefix='conf_res'):
    game_code:str


class CancelResetGame_CallbackData(CallbackData, prefix='canc_res'):
    ok:str

class BackResetGame_CallbackData(CallbackData, prefix='back_to_res'):
    ok:str

class BackToTypesFromGenre_CallbackData(CallbackData, prefix='back_to_types'):
    ok:str


start_btn = InlineKeyboardButton(text='Начать', callback_data='start_play_game')
start_game = InlineKeyboardBuilder().add(start_btn).as_markup()

class GetUserGroup_CallbackData(CallbackData, prefix='user_group'):
    group_name:str
    page:int

class BackToUserGroup_CallbackData(CallbackData, prefix='back_to_user_groups'):
    back:str

class AddToUserGroup_CallbackData(CallbackData, prefix='add_to_user_group'):
    game_code:str

class RemoveFromUserGroup_CallbackData(CallbackData, prefix='remove_from_user_group'):
    game_code:str

class ControlUserGroup_CallbackData(CallbackData, prefix='control_user_group'):
    game_code:str

class ChooseGroupAdd_CallbackData(CallbackData, prefix='g_a'):
    game_code:str
    group_name:str

class ChooseGroupRemove_CallbackData(CallbackData, prefix='g_r'):
    game_code:str
    group_name:str

class CreateNewUserGroup_CallbackData(CallbackData, prefix='create_user_group'):
    game_code:str

class GetUserGroupForReset_CallbackData(CallbackData, prefix='gugfr'):
    group_name:str

##Agreement
paper = InlineKeyboardButton(text='Пользовательское соглашение', url='https://telegra.ph/Polzovatelskoe-soglashenie-06-21-6')
agree = InlineKeyboardButton(text='Принять ✅', callback_data=PaperAgree_CallbackData(agree='ye').pack())

agreement_ikb = InlineKeyboardBuilder().add(paper).add(agree).as_markup()

##Main kb
main_kb_builder = ReplyKeyboardBuilder()
about_me = KeyboardButton(text=phr.profile)
library = KeyboardButton(text=phr.library)
shop = KeyboardButton(text=phr.shop)
about_us = KeyboardButton(text=phr.about_us)
main_kb_builder.row(library,shop).row(about_us,about_me)
main_kb = main_kb_builder.as_markup(resize_keyboard=True)


##Shop kb
store = KeyboardButton(text=phr.store)
find_game = KeyboardButton(text=phr.search_game)
shop_statistic = KeyboardButton(text=phr.shop_statistic)
main_menu = KeyboardButton(text=phr.main_menu)
shop_kb_builder = ReplyKeyboardBuilder()
shop_kb_builder.add(store,find_game).row(shop_statistic,main_menu)
shop_kb = shop_kb_builder.as_markup(resize_keyboard=True)



##profile keyboard
back_to_profile = InlineKeyboardButton(text='Назад ↩️', callback_data=ProfileAction_CallbackData(action='back_to_profile').pack())
back_to_games = InlineKeyboardButton(text='Назад ↩️',callback_data=ProfileAction_CallbackData(action='back_to_games').pack())
show_achivements = InlineKeyboardButton(text='Показать достижения ✅ ', callback_data=ProfileAction_CallbackData(action='show_achivements').pack())
bad_achivements = InlineKeyboardButton(text='У вас нет достижений ❌', callback_data=ProfileAction_CallbackData(action='no_achivements').pack())



profile_kb_have_achivements_builder = InlineKeyboardBuilder().add(show_achivements)
profile_kb_have_achivements = profile_kb_have_achivements_builder.as_markup()
profile_kb_not_have_achivements_builder = InlineKeyboardBuilder().add(bad_achivements)
profile_kb_not_have_achivements = profile_kb_not_have_achivements_builder.as_markup()



def return_games_btn_achivement(games):
    if games != 0:
        markup = InlineKeyboardBuilder()
        for i in games:
            game = db.return_game_info(i)
            markup.row(InlineKeyboardButton(text=game['game_name'], callback_data=ProfileAchivementGames_CallbackData(game_code=i).pack()))
        return markup


def return_achivements(achivments,game_code):
    markup = InlineKeyboardBuilder()
    for i in achivments:
        achivment = db.return_achivement(game_code=game_code, achivement_code=i)
        if achivment != 0:
            markup.row(InlineKeyboardButton(text=achivment["name"], callback_data=ProfileAchivementCode_CallbackData(game_code=game_code,achivement_code=achivment['achivement_code']).pack()))
    return markup


def return_library(games, type='lib',page=0, category_code=None, type_code=None):
    markup = InlineKeyboardBuilder()
    if len(games) <= 5:
        if games != 0:
            for i in games:
                markup.row(InlineKeyboardButton(text=i['game_name'], callback_data=ShowMoreInfoGame_CallbackData(game_code=i['game_code']).pack()))
    else:
        counter = len(games)//5
        if len(games)%5 !=0:
            counter+=1
        games = games[5*page:5*page+5]
        for i in games:
            markup.row(InlineKeyboardButton(text=i['game_name'], callback_data=ShowMoreInfoGame_CallbackData(game_code=i['game_code']).pack()))
        match type:
            case 'store':
                page_counter = InlineKeyboardButton(text=f'{page + 1}/{counter}',
                                                    callback_data=GetAllPages_CallbackData(type=type, type_code=type_code, category_code=category_code).pack())

                if page > 0:
                    back_btn = InlineKeyboardButton(text='⬅️', callback_data=ShowMoreGameGenre_CallbackData(type_code=type_code,genre_code=category_code,page=page-1).pack())
                else:
                    back_btn = InlineKeyboardButton(text='⬅️', callback_data=EndList_CallbackData(info='bad').pack())

                if 5*(page+1) in range(len(games)+1):
                    next_btn = InlineKeyboardButton(text='➡️', callback_data=ShowMoreGameGenre_CallbackData(type_code=type_code,genre_code=category_code,page=page+1).pack())
                else:
                    next_btn = InlineKeyboardButton(text='➡️', callback_data=EndList_CallbackData(info='bad').pack())
                markup.row(back_btn,
                           page_counter,
                           next_btn)
            case 'lib':
                page_counter = InlineKeyboardButton(text=f'{page + 1}/{counter}',
                                                    callback_data=GetAllPages_CallbackData(type=type, type_code='n', category_code=category_code).pack())

                if page > 0:
                    back_btn = InlineKeyboardButton(text='⬅️',
                                                    callback_data=GetUserGroup_CallbackData(group_name=category_code, page=page - 1).pack())
                else:
                    back_btn = InlineKeyboardButton(text='⬅️',
                                                    callback_data=EndList_CallbackData(info='bad').pack())

                if 5 * (page + 1) in range(len(games)+1):
                    next_btn = InlineKeyboardButton(text='➡️', callback_data=
                        GetUserGroup_CallbackData(group_name=category_code, page=page+1).pack())
                else:
                    next_btn = InlineKeyboardButton(text='➡️', callback_data=
                        EndList_CallbackData(info='bad').pack())

                markup.row(back_btn,
                           page_counter,
                           next_btn)
    return markup

def lib_category(categories):
    markup = InlineKeyboardBuilder()
    for key,_ in categories.items():
        markup.row(InlineKeyboardButton(text=key, callback_data=GetUserGroup_CallbackData(group_name=key, page=0).pack()))
    return markup
def reset_library(games):
    markup = InlineKeyboardBuilder()
    if games !=0 :
        for i in games:
            markup.row(InlineKeyboardButton(text=i['game_name'], callback_data=ResetGame_CallbackData(game_code=i['game_code']).pack()))
    return markup
def reset_library_categories(categories):
    markup = InlineKeyboardBuilder()
    if categories != 0 :
        for key, _ in categories.items():
            markup.row(InlineKeyboardButton(text=key, callback_data=GetUserGroupForReset_CallbackData(group_name=key).pack()))
    return markup

def store_kb_genres(genre, type_code):
    markup = InlineKeyboardBuilder()
    btn = []
    for i in genre:
        btn.append(InlineKeyboardButton(text=db.return_genre_name_by_code(i, type_code=type_code),callback_data=ShowMoreGameGenre_CallbackData(type_code=type_code,genre_code=i,page=0).pack()))

    markup.row(*btn,width=1)

    return markup

def store_kb_types(type):
    markup = InlineKeyboardBuilder()
    btn = []
    for i in type:
        btn.append(InlineKeyboardButton(text=db.return_type_name_by_code(i),callback_data=ShowGenresByType_CallbackData(type_code=i).pack()))
    markup.row(*btn,width=1)
    return markup
def get_game(game_code:str, have_it_user:int, price:int, user_id:int):
    check_frame = db.return_frame(1,game_code)
    game = db.return_game_info(game_code)
    markup = InlineKeyboardBuilder()
    game_cfg = db.return_game_cfg(user_id, game_code)
    user = db.return_user_info(user_id)
    if check_frame != 0 and game['can_buy'] != 0:
        match have_it_user:
            case 1 if not game_cfg or game_cfg['is_demo'] == 0:
                markup.row(InlineKeyboardButton(text='Запустить 🎮', callback_data=PlayingGame_CallbackData(game_code=game_code).pack()), InlineKeyboardButton(text='Оценить 🌟', callback_data=RateGame_CallbackData(game_code=game_code).pack()))
            case _:
                match price:
                    case 0:
                        markup.row(InlineKeyboardButton(text='Получить 👇', callback_data=BuyGame_CallbackData(game_code=game_code).pack()))
                    case _:
                            btns = []
                            if game_cfg == 0:
                                btns.append(InlineKeyboardButton(text='Купить 💳', callback_data=BuyGame_CallbackData(game_code=game_code).pack()))
                            elif game_cfg['is_demo'] == 1:
                                btns.append(InlineKeyboardButton(text='Купить полную версию 💳', callback_data=BuyGame_CallbackData(game_code=game_code).pack()))
                            if game_cfg == 0:
                                btns.append(InlineKeyboardButton(text='Получить демо 👇', callback_data=GetDemo_CallbackData(game_code=game_code).pack()))
                            else:
                                btns.append(InlineKeyboardButton(text='Запустить 🎮', callback_data=PlayingGame_CallbackData(game_code=game_code).pack()))
                            markup.row(*btns)
    else:
        if have_it_user == 0:
            markup.row(InlineKeyboardButton(text='Продукт недоступен ❌', callback_data=UnavailableGame_CallbackData(game_code=game_code).pack()))
        else:
            markup.row(InlineKeyboardButton(text='Запустить 🎮', callback_data=PlayingGame_CallbackData(game_code=game_code).pack()), InlineKeyboardButton(text='Оценить 🌟', callback_data=RateGame_CallbackData(game_code=game_code).pack()))

    if user['is_admin'] == 1:
        markup.row(InlineKeyboardButton(text=phr.statistic,callback_data=GameStatistic_CallbackData(game_code=game_code).pack()))

    if have_it_user == 1:
        markup.row(InlineKeyboardButton(text=phr.control_user_group, callback_data=ControlUserGroup_CallbackData(game_code=game_code).pack()))

    elif db.get_user_group_by_game(user_id, game_code, 0):
        markup.row(InlineKeyboardButton(text=phr.remove_from_user_group, callback_data=RemoveFromUserGroup_CallbackData(game_code=game_code).pack()))

    if price == 0 and have_it_user == 1:
        markup.row(InlineKeyboardButton(text=phr.delete_game_from_lib, callback_data=DeleteGameFromLibrary_CallbackData(game_code=game_code).pack()))
    markup.row(InlineKeyboardButton(text=phr.share_game, switch_inline_query=game['game_name']))

    return markup

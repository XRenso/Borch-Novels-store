from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import phrase as phr
from aiogram.dispatcher import FSMContext


@dp.callback_query_handler(kb.admin_frame_info.filter())
async def show_frame_info_admin(call:types.CallbackQuery, callback_data: dict, state:FSMContext):
    game = db.return_game_info(callback_data['game_code'])
    frame = db.return_frame(int(callback_data['frame_num']), game['game_code'])
    match frame['content_code']:
        case 1:
            content = 'Изображение'
        case 2:
            content = 'Видео'
        case 3:
            content = 'Аудио'
        case 4:
            content = 'Гиф'
        case _:
            content = 'Текст'
    if frame['is_demo']:
        demo = 'Кадр является демо'
    else:
        demo = 'Кадр не является демо'
    variants = 'Варианты кадра:\n<i>Номер кадра</i> => <i>Текст кнопки</i>\n'
    for key,val in frame['variants'].items():
        variants += f'{key} => {val}\n'
    if frame['change_add_conditions']:
        change_conditions = 'Кадр изменяет конфиг:\n'
        for i in change_conditions.split('\n'):
            change_conditions += f'{i}\n'
    else:
        change_conditions = 'Кадр не изменяет конфиг\n'

    if frame['check_add_conditions']:
        check_conditions='Кадр проверяет следующие условия:\n'
        for i in frame['check_add_conditions'].split('\n'):
            check_conditions += f'{i}\n'
        check_conditions+=f'В случае проверки приведет в кадр - {frame["fail_condition_frame"]}'
    else:
        check_conditions='Кадр не проверяет никакие условия'

    info = f'<i>Название продукта</i> - {game["game_name"]}\n' \
           f'Номер кадра - {callback_data["frame_num"]}\n\n' \
           f'Содержимое - <i>{content}</i>\n\n' \
           f'{demo}\n\n' \
           f'{variants}\n' \
           f'Имеет ли доп. сообщение звука - {"Да" if frame["sound"] else "Нет"}\n\n' \
           f'Есть ли доп. сообщение стикер - {"Да" if frame["sticker"] else "Нет"}\n\n' \
           f'{change_conditions}\n' \
           f'{check_conditions}\n\n' \
           f'Код достижения - <i>{frame["achivement"] if frame["achivement"] else "Кадр не дает достижения"}</i>\n\n' \
           f'Полный json кадра:\n<code>{frame}</code>'

    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back_to_game,callback_data=kb.play_game.new(game['game_code'])))

    try:
        await call.message.edit_text(info, parse_mode='HTML',reply_markup=markup)
    except:
        await call.message.edit_caption(info, parse_mode='HTML',reply_markup=markup)
from loader import dp,db
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
import phrase as phr
from aiogram.types import InputMediaPhoto
@dp.callback_query_handler(kb.profile_achivement_code.filter())
async def achivement_info(call:types.CallbackQuery, callback_data: dict):
    info = callback_data['achivement_code'].split('<@')
    game_code = info[0]
    achivement_code = info[1]
    achivement  = db.return_achivement(game_code,achivement_code)
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.profile_achivement_games.new(achivement['game_code'])))
    content = InputMediaPhoto(media=achivement['cover'], caption=f'Достижение ✅ - {achivement["name"]}\nОписание:\n{achivement["description"]}')
    await call.message.edit_media(content, reply_markup=markup)

@dp.callback_query_handler(kb.profile_achivement_games.filter())
async def achivments_games(call:types.CallbackQuery, callback_data: dict):
    markup = kb.return_achivements(db.return_user_achivement_by_game_code(call.message.chat.id,callback_data['game_code']), game_code=callback_data['game_code']).add(kb.back_to_games)
    try:
        content = InputMediaPhoto(media='AgACAgIAAxkBAAIlSWS0kvTmnIDiPDrB9RKkNIAyyqgnAAPPMRtYW6FJ1ybBvzYseRYBAAMCAAN5AAMvBA', caption='Выберите интересующее вас достижение 🤔')
        await call.message.edit_media(content, reply_markup=markup)
    except:
        await call.message.delete()
        await call.message.answer_photo(photo='AgACAgIAAxkBAAIlSWS0kvTmnIDiPDrB9RKkNIAyyqgnAAPPMRtYW6FJ1ybBvzYseRYBAAMCAAN5AAMvBA',caption='Выберите интересующее вас достижение 🤔', reply_markup=markup)

@dp.callback_query_handler(kb.profile_action.filter())
async def profile_menu(call:types.CallbackQuery, callback_data: dict):
    match callback_data['action']:
        case 'show_achivements':
            markup = kb.return_games_btn_achivement(db.return_user_games_with_achivement(call.message.chat.id)).add(kb.back_to_profile)
            content = InputMediaPhoto(media='AgACAgIAAxkBAAIlSWS0kvTmnIDiPDrB9RKkNIAyyqgnAAPPMRtYW6FJ1ybBvzYseRYBAAMCAAN5AAMvBA', caption='Выберите игру, в которой хотите увидеть ваши достижения 👇')
            await call.message.edit_media(content, reply_markup=markup)
        case 'back_to_profile':
            user_info = db.return_user_info(call.message.chat.id)
            curr_game = db.return_game_info(user_info['curr_game_code'])
            if curr_game == 0:
                curr_game = 'К сожалению вы не проходите сейчас какую-либо игру ❌'
            else:
                curr_game = curr_game['game_name']

            achivments = user_info['achivements']
            markup = kb.profile_kb_have_achivements
            if len(achivments) < 1:
                achivments = 'У вас нет достижений ❌'
                markup = kb.profile_kb_not_have_achivements

            await call.message.edit_media(media=InputMediaPhoto(media='AgACAgIAAxkBAAIlRGS0kvTRaTvuTMIEHLw6pM_Se0S3AAL7zjEbWFuhSQhs6LkM8O3DAQADAgADeQADLwQ',caption=f'Ваш id - {user_info["user_id"]}'
                                         f'\nКоличество игр в библиотеке 📂- {len(db.return_user_library_games(call.message.chat.id))}'
                                         f'\nВы проходите 🎮 - {curr_game}'
                                         f'\nКоличество ваших достижений 🌟 - '
                                         f'{len(achivments)}'),
                                                reply_markup=markup)


        case 'back_to_games':
            markup = kb.return_games_btn_achivement(db.return_user_games_with_achivement(call.message.chat.id)).add(kb.back_to_profile)
            await call.message.edit_caption('Выберите игру, в которой хотите увидеть ваши достижения 👇', reply_markup=markup)
        case 'no_achivements':
            await call.message.edit_caption('К сожалению у вас нет достижений ❌.\nИграйте в игры, чтобы их получить 🎮')

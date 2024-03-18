from loader import dp,db
from aiogram import types
import keyboards as kb
import phrase as phr
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.filters.command import Command
@dp.message(Command('start'))
async def start(message: types.Message):
    user = db.return_user_info(message.from_user.id)
    if user != 0 and user['accept_paper'] == 1:
        await message.answer_photo(photo='AgACAgIAAxkBAAIZlGSSdZ8ekz_L3D1UdfCD_2cKPV97AAJNxzEbVxOYSDqKrtfuwW3mAQADAgADeQADLwQ',
                                   caption= f'Здравствуй, {message.from_user.first_name}! 🎁 \n'
                                f'\nДобро пожаловать в магазин Borch Store.\n'
                             f'\n🔱 Используйте меню, для взаимодействия с ботом.', reply_markup=kb.main_kb)

        try:
            game_code = message.get_args()
            if game_code is not None:
                game = db.return_game_info(game_code)
                media = MediaGroupBuilder()
                if db.return_user_info(message.from_user.id) != 0:
                    try:
                        markup = kb.get_game(game['game_code'],
                                             db.check_is_game_in_user_library(message.from_user.id, game['game_code']), game['price'],
                                             user_id=message.from_user.id)
                    except TypeError:
                        return
                    for index, file_id in enumerate(game['game_cover'].split('\n')):
                        match index:
                            case _:
                                match file_id.lower()[0]:
                                    case 'b':
                                        media.add_video(media=file_id)
                                    case 'a':
                                        media.add_photo(media=file_id)

                    game_info_text = phr.get_product_info(game)
                    await message.answer_media_group(media=media.build())
                    await message.answer(game_info_text, reply_markup=markup.as_markup())
        except AttributeError:
            pass
    else:
        await message.answer('Ознакомиться с правилами можно по кнопке ниже: ', reply_markup=kb.agreement_ikb)


@dp.callback_query(kb.PaperAgree_CallbackData.filter())
async def agree_paper(call:types.CallbackQuery, callback_data:kb.PaperAgree_CallbackData):
    await call.message.edit_text('Успешно принято соглашение ✅. \nПриятной эксплуатации магазина 🎊')
    if db.add_user(call.message.chat.id) == 0:
        db.accepted_paper(call.message.chat.id)
    await call.message.answer_photo(
        photo='AgACAgIAAxkBAAIZlGSSdZ8ekz_L3D1UdfCD_2cKPV97AAJNxzEbVxOYSDqKrtfuwW3mAQADAgADeQADLwQ',
        caption=f'Здравствуй, {call.message.from_user.first_name}! 🎁 \n'
                f'\nДобро пожаловать в магазин Borch Store.\n'
                f'\n🔱 Используйте меню, для взаимодействия с ботом.', reply_markup=kb.main_kb)
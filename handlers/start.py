from loader import dp,db
from aiogram import types
import keyboards as kb
@dp.message_handler(commands = ['start'])
async def start(message: types.Message):
    user = db.return_user_info(message.from_user.id)
    if user != 0 and user['accept_paper'] == 1:

        await message.answer_photo(photo='AgACAgIAAxkBAAIZlGSSdZ8ekz_L3D1UdfCD_2cKPV97AAJNxzEbVxOYSDqKrtfuwW3mAQADAgADeQADLwQ',
                                   caption= f'Здравствуй, {message.from_user.first_name}! 🎁 \n'
                                f'\nДобро пожаловать в магазин Borch Store.\n'
                             f'\n🔱 Используйте меню, для взаимодействия с ботом.', reply_markup=kb.main_kb)
    else:
        await message.answer('Ознакомиться с правилами можно по кнопке ниже: ', reply_markup=kb.agreement_ikb)


@dp.callback_query_handler(kb.paper_cb.filter())
async def agree_paper(call:types.CallbackQuery, callback_data:dict):
    await call.message.edit_text('Успешно принято соглашение ✅. \nПриятной эксплуатации магазина 🎊')
    if db.add_user(call.message.chat.id) == 0:
        db.accepted_paper(call.message.chat.id)
    await call.message.answer_photo(
        photo='AgACAgIAAxkBAAIZlGSSdZ8ekz_L3D1UdfCD_2cKPV97AAJNxzEbVxOYSDqKrtfuwW3mAQADAgADeQADLwQ',
        caption=f'Здравствуй, {call.message.from_user.first_name}! 🎁 \n'
                f'\nДобро пожаловать в магазин Borch Store.\n'
                f'\n🔱 Используйте меню, для взаимодействия с ботом.', reply_markup=kb.main_kb)
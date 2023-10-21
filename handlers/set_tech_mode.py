from loader import dp,db
from aiogram import types

@dp.message_handler(commands = ['set_tech_mode'])
async def i_want_tech_mode(message: types.Message):
    user = db.return_user_info(message.from_user.id)
    if user['is_admin']:
        db.change_tech_mode_server(not db.is_bot_in_tech_mode())
        add = 'функционирования'
        if db.is_bot_in_tech_mode():
            add = 'техобслуживания'

        await message.answer(f'Сервер успешно перешел в состояние - {add}')
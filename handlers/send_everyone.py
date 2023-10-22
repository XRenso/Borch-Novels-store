from loader import dp,db,bot
from states.Admin import Admin
from aiogram import types
from aiogram.dispatcher import FSMContext
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



@dp.message_handler(commands = ['send_everyone'])
async def send_everyone(message: types.Message):
    user = db.return_user_info(message.from_user.id)
    if user['is_admin']:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Да✅', callback_data=kb.send_everyone.new('yes')))
        markup.add(InlineKeyboardButton('Нет❌', callback_data=kb.send_everyone.new('no')))

        await message.answer('Вы уверены, что хотите сделать рассылку?', reply_markup=markup)

@dp.callback_query_handler(kb.send_everyone.filter())
async def send_everyone_handler(call:types.CallbackQuery, callback_data: dict):
    status = callback_data['confirm']

    if status == 'yes':
        await call.message.edit_text('Отправьте сообщение для рассылки.\nОтменить ввод можно командой - /cancel')
        await Admin.send_message.set()
    elif status == 'no':
        await call.message.edit_text('Успешно отменена рассылка')

@dp.message_handler(state=Admin.send_message,content_types=[
            types.ContentType.PHOTO,
            types.ContentType.DOCUMENT,
            types.ContentType.TEXT,
            types.ContentType.AUDIO,
            types.ContentType.VOICE,
            types.ContentType.VIDEO,
            types.ContentType.ANIMATION,
            types.ContentType.STICKER
        ])
async def send_message(message: types.Message, state: FSMContext):
    msg = message.text
    if msg != '/cancel':
        await bot.copy_message(
            chat_id=message.from_user.id,
            from_chat_id=message.from_user.id,
            message_id=message.message_id
        )
        # users_id = db.get_all_users_id()
        # for i in users_id:
        #     await bot.copy_message(
        #         chat_id=i,
        #         from_chat_id=message.from_user.id,
        #         message_id=message.message_id
        #     )
    else:
        await message.answer('Успешная отмена ❌')
    await state.finish()


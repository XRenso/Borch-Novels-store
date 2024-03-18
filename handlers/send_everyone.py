from loader import dp,db,bot
from states.Admin import Admin
from aiogram import types, F
from aiogram.fsm.context import FSMContext
import keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton
from aiogram.filters.command import Command


@dp.message(Command('send_everyone'))
async def send_everyone(message: types.Message):
    user = db.return_user_info(message.from_user.id)
    if user['is_admin']:
        markup = InlineKeyboardBuilder()
        markup.add(InlineKeyboardButton(text='Да✅', callback_data=kb.RSS_CallbackData(confirm='yes').pack()))
        markup.add(InlineKeyboardButton(text='Нет❌', callback_data=kb.RSS_CallbackData(confirm='no').pack()))

        await message.answer('Вы уверены, что хотите сделать рассылку?', reply_markup=markup.as_markup())

@dp.callback_query(kb.RSS_CallbackData.filter())
async def send_everyone_handler(call:types.CallbackQuery, callback_data: kb.RSS_CallbackData, state:FSMContext):
    status = callback_data.confirm

    if status == 'yes':
        await call.message.edit_text('Отправьте сообщение для рассылки.\nОтменить ввод можно командой - /cancel')
        await state.set_state(Admin.send_message)
    elif status == 'no':
        await call.message.edit_text('Успешно отменена рассылка')

@dp.message(Admin.send_message, F.any)
async def send_message(message: types.Message, state: FSMContext):
    msg = message.text
    if msg != '/cancel':
        # await bot.copy_message(
        #     chat_id=message.from_user.id,
        #     from_chat_id=message.from_user.id,
        #     message_id=message.message_id
        # )
        await message.answer('Рассылка отправлена ✅')
        users_id = db.get_all_users_id()
        for i in users_id:
            try:
                await bot.copy_message(
                    chat_id=i,
                    from_chat_id=message.from_user.id,
                    message_id=message.message_id
                )
            except:
                pass
    else:
        await message.answer('Успешная отмена ❌')

    await state.clear()


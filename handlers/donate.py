from loader import dp
from aiogram import types
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice
import os
@dp.message_handler(commands = ['donate'])
async def donation_handler(message:types.Message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Поддержать',callback_data=kb.donate.new('donate')))
    await message.answer(f'Поддержать проект по кнопке ниже👇', reply_markup=markup)


@dp.callback_query_handler(kb.donate.filter())
async def donate_us(call:types.CallbackQuery, callback_data:dict):
    try:
        await call.message.delete()
    except:
        pass
    await call.bot.send_invoice(
                chat_id=call.message.chat.id,
                title= f'Пожертвование на развитие сервера',
                description=f'Эти средства нам помогут развивать свой проект дальше.',
                payload=f'donation',
                provider_token=os.getenv('KASSA'),
                currency='rub',
                prices=[
                    LabeledPrice(
                        label='Поддержка авторов',
                        amount=110*100
                    ),
                ],
                max_tip_amount=1500*100,
                suggested_tip_amounts=[150*100,300*100,500*100,1000*100],
                start_parameter='no',
                provider_data=None,
                need_name=False,
                need_email=False,
                need_phone_number=False,
                need_shipping_address=False,
                send_phone_number_to_provider=False,
                send_email_to_provider=False,
                is_flexible=False,
                disable_notification=False,
                protect_content=False,
                reply_to_message_id=False,
                allow_sending_without_reply=True,
                reply_markup=None,

            )
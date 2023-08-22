from loader import dp,db,bot
from aiogram import types
import keyboards as kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice,PreCheckoutQuery
import os
import phrase as phr

@dp.callback_query_handler(kb.buy_game.filter())
async def buy_game(call:types.CallbackQuery, callback_data: dict):
    game_code = callback_data['game_code']
    game = db.return_game_info(game_code)
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton(phr.back_to_game, callback_data=kb.get_game_info.new(callback_data['game_code'])))
    match game['price']:
        case 0:
            db.give_game_to_user(game_code,call.message.chat.id, 0)
            db.update_month_game_sales(game['game_code'])
            try:
                await call.message.edit_text(f'{game["game_name"]} успешно добавлена в библиотеку ✅', reply_markup=markup)
            except:
                await call.message.delete()
                await call.message.answer(f'{game["game_name"]} успешно добавлена в библиотеку ✅', reply_markup=markup)
        case _:
            try:
                await call.message.delete()
            except:
                pass
            await call.bot.send_invoice(
                chat_id=call.message.chat.id,
                title= f'Покупка игры {game["game_name"]}',
                description=game['game_description'],
                payload=f'buy@{game["game_code"]}',
                provider_token=os.getenv('KASSA'),
                currency='rub',
                prices=[
                    LabeledPrice(
                        label='Доступ к игре',
                        amount=game['price']*100
                    ),
                    LabeledPrice(
                        label='Скидка',
                        amount=-game['discount'] * 100
                    )
                ],
                max_tip_amount=1000*100,
                suggested_tip_amounts=[50*100,100*100,150*100,300*100],
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

@dp.pre_checkout_query_handler()
async def give_paid_game_to_user(pre_checkout_query:PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id,ok=True)
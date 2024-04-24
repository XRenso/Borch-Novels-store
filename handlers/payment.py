from loader import dp,db
from aiogram import types, F
import phrase as phr
import keyboards as kb
from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton

@dp.message(F.successful_payment)
async def uspeh_buy(message:types.Message):
    info = message.successful_payment.invoice_payload.split('@')
    operation = info[0]
    match operation:
        case 'buy':
            game = db.return_game_info(info[1])
            db.give_game_to_user(game['game_code'], message.from_user.id, 0)
            db.update_month_game_sales(game['game_code'])
            markup = InlineKeyboardBuilder().add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game['game_code']).pack()))

            await message.answer(f'Благодарим вас за покупку на сумму {message.successful_payment.total_amount//100} руб.'
                                 f'\n Игра - {game["game_name"]}  - успешно добавлена в вашу библиотеку ✅', reply_markup=markup.as_markup())
        case 'donation':
            await message.answer(f'Спасибо за вашу поддержку на {message.successful_payment.total_amount//100} руб. \nЭти деньги помогут нам в развитии проекта')

@dp.callback_query(kb.GetDemo_CallbackData.filter())
async def get_demo(call:types.CallbackQuery, callback_data:kb.GetDemo_CallbackData):
    game_code = callback_data.game_code
    game = db.return_game_info(game_code)
    db.give_game_to_user(game_code=game_code,user_id=call.message.chat.id,is_demo=1)
    markup = InlineKeyboardBuilder().add(InlineKeyboardButton(text=phr.back_to_game,
                                                              callback_data=kb.GetGameInfo_CallbackData(
                                                                  game_code=game['game_code']).pack()))
    await call.message.edit_text(f'Демо-версия успешно «{game["game_name"]}» добавлена в вашу библиотеку✅',reply_markup=markup.as_markup())
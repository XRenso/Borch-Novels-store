from loader import dp,db
from aiogram import types
import keyboards as kb
import phrase as phr
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

@dp.callback_query(kb.RateGame_CallbackData.filter())
async def rating_game(call:types.CallbackQuery, callback_data:kb.RateGame_CallbackData):
    markup = InlineKeyboardBuilder()
    btn = []
    for i in range(5):
        btn.append(InlineKeyboardButton(text=f'{i+1}', callback_data=kb.Rating_CallbackData(game_code=callback_data.game_code,score=i+1).pack()))
    markup.row(*btn,width=5)
    markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=callback_data.game_code).pack()))
    await call.message.edit_text('Выберите оценку', reply_markup=markup.as_markup())
@dp.callback_query(kb.Rating_CallbackData.filter())
async def rate_game(call:types.CallbackQuery, callback_data:kb.Rating_CallbackData):
    game_code = callback_data.game_code
    score = callback_data.score
    db.rate_game(call.message.chat.id, game_code, score)
    markup = InlineKeyboardBuilder().add(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game_code).pack()))
    await call.message.edit_text('Успешно поставлена оценка', reply_markup=markup.as_markup())
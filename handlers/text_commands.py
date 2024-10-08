from loader import dp,db
from aiogram import types, F
import phrase as phr
import keyboards as kb
from states.Store import Store
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardButton, KeyboardButton)
@dp.message(F.text)
async def get_text(message: types.Message, state:FSMContext):
    user = db.return_user_info(message.from_user.id)
    if user != 0 and user['accept_paper'] == 1:
        match message.text:
            case phr.library:
                markup = kb.return_library(db.return_user_library_games(message.from_user.id), page=0, type='lib',category_code='Все игры')

                if not len(markup.as_markup().inline_keyboard):
                    await message.answer_photo(photo='AgACAgIAAxkBAAIwh2TlvPH-RIgfxZAjx5qUZJ8SXHa2AAKq2TEbo4EhS_6Xi0_d9uahAQADAgADeQADMAQ',caption='У вас нет игр ❌')
                else:
                    if len(user['user_groups']) == 1:
                        await message.answer_photo(photo='AgACAgIAAxkBAAIwh2TlvPH-RIgfxZAjx5qUZJ8SXHa2AAKq2TEbo4EhS_6Xi0_d9uahAQADAgADeQADMAQ',caption='Ваша библиотека 📂', reply_markup=markup.as_markup())
                    else:
                        await message.answer_photo(
                            photo='AgACAgIAAxkBAAIwh2TlvPH-RIgfxZAjx5qUZJ8SXHa2AAKq2TEbo4EhS_6Xi0_d9uahAQADAgADeQADMAQ',
                            caption='Ваша библиотека 📂', reply_markup=kb.lib_category(user['user_groups']).as_markup())

            case phr.profile:
                user_info = db.return_user_info(message.from_user.id)
                if user_info != 0:
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
                    await message.answer_photo(photo='AgACAgIAAxkBAAIlRGS0kvTRaTvuTMIEHLw6pM_Se0S3AAL7zjEbWFuhSQhs6LkM8O3DAQADAgADeQADLwQ',
                                               caption=f'Ваш id - {user_info["user_id"]}'
                                         f'\nКоличество игр в библиотеке 📂- {len(db.return_user_library_games(message.from_user.id))}'
                                         f'\nВы заняты 🌐 - {curr_game}'
                                         f'\nКоличество ваших достижений 🌟 - '
                                         f'{len(achivments)}', reply_markup=markup)
                else:
                    await message.answer('Пройдите регистрацию. Отправив сообщение /start')

            case phr.search_game:
                await message.answer('Отправьте название игры, которую хотите найти. \nОтправьте /cancel для отмены')

                await state.set_state(Store.search_game)

            case phr.store:
                types = db.return_type()
                markup = kb.store_kb_types(types)
                if not len(markup.as_markup().inline_keyboard):
                    await message.answer(f'Отсутствует товар в магазине ❌')
                else:
                    await message.answer_photo(photo='AgACAgIAAxkBAAIlRmS0kvRiHbkGzpyvclOYwC94Wfb8AAL9zjEbWFuhSWJYQDJSBo2bAQADAgADeQADLwQ',caption=f'Выберите интересующую вас категорию 👇', reply_markup=markup.as_markup())

            case phr.shop:
                await message.answer_photo(photo='AgACAgIAAxkBAAIlSGS0kvRFxrhXUkBn47w7TfhKssj7AAL_zjEbWFuhSVPyV3miV65oAQADAgADeQADLwQ',caption='Выберите интересующую вас функцию 👇 ', reply_markup=kb.shop_kb)
            case phr.main_menu:
                await message.answer('Добро пожаловать на главное меню ✨', reply_markup=kb.main_kb)
            case phr.shop_statistic:
                await message.answer(db.bot_statistic())
            case phr.about_us:
                markup = InlineKeyboardBuilder()
                tg_chanel = InlineKeyboardButton(text='Телеграм-канал', url='https://t.me/BorchStore')
                designer = InlineKeyboardButton(text='Дизайнер', url='https://t.me/cuddies19')
                programmist = InlineKeyboardButton(text='Программист', url='https://t.me/XRenso')
                user_paper = InlineKeyboardButton(text='Пользовательское соглашение', url='https://telegra.ph/Polzovatelskoe-soglashenie-06-21-6')
                markup.add(user_paper)
                # markup.row(designer,programmist)
                markup.row(tg_chanel)

                await message.answer_photo(photo='AgACAgIAAxkBAAIlRWS0kvQ3UB9D23YElI6zwb_iEr40AAL8zjEbWFuhSaYY_HtSoELTAQADAgADeQADLwQ',caption=phr.info, reply_markup=markup.as_markup())
    else:
        await message.answer('Ознакомиться с правилами можно по кнопке ниже: ', reply_markup=kb.agreement_ikb)

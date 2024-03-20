from loader import dp,db
import keyboards as kb
from aiogram.utils.keyboard import (ReplyKeyboardBuilder, InlineKeyboardBuilder,
                                    InlineKeyboardButton, KeyboardButton)
from aiogram import types
import phrase as phr
from aiogram.types import InputMediaPhoto, InputMediaVideo, InputMediaAudio, InputMediaAnimation
from states.Store import Store
from aiogram.fsm.context import FSMContext
import small_logic as s_log
async def change_frames(call, frame_num, state:FSMContext, failed:int=0):
    user = db.return_user_info(call.message.chat.id)
    game = db.return_game_info(user['curr_game_code'])
    game_cfg = db.return_game_cfg(user['user_id'], game['game_code'])
    data = await state.get_data()
    frame = db.return_frame(frame_num=frame_num, game_code=game['game_code'])
    can_next = True
    if not failed:
        now_frame_vars = db.return_frame(game_cfg["frame_num"], game["game_code"])["variants"]
        try:
            now_frame_vars[str(frame_num)]
        except:
            try:
                await call.message.edit_text("Сессия устарела\nЗапустите игру заново 🔁")
            except:
                await call.message.edit_caption(caption="Сессия устарела\nЗапустите игру заново 🔁",reply_markup=None)
            return
    if frame != 0 and frame['fail_condition_frame'] is not None and frame['check_add_conditions'] is not None:
        conditions = frame['check_add_conditions'].split('\n')
        for i in conditions:
            info = i.split(':')
            key = info[0]
            value = info[1]
            cfg = db.return_game_cfg(call.message.chat.id, game['game_code'])
            if cfg[key] != value:
                # frame = db.return_frame(frame_num=frame['fail_condition_frame'], game_code=game['game_code'])
                await change_frames(call, frame['fail_condition_frame'], state, failed=1)
                can_next = False
                break

    if data.get('achivement') is not None:
        try:
            await call.bot.delete_message(message_id=data.get('achivement').message_id, chat_id=call.message.chat.id)
        except:
            pass
    if data.get('game_text') is not None and data.get('game_text').message_id != call.message.message_id:
        try:
            await call.message.edit_text('Сессия устарела\nЗапустите игру заново 🔁')
        except:
            await call.message.delete()
            await call.message.answer('Сессия устарела \nЗапустите игру заново 🔁')
    else:
        if frame != 0 and can_next:
            if game_cfg['is_demo'] <= frame['is_demo']:
                db.update_user_frame_num(user['user_id'], frame_num, game['game_code'])
                frame_text = frame['text']['ru']
                if game['can_change_page']:
                    frame_text = f"{frame_text}\n\n" \
                                 f"Страница {frame['frame_num']} из {db.return_number_of_frames(game_code=game['game_code'])}"

                match frame['content_code']:
                    case 1:
                        content = InputMediaPhoto(media=frame['content'], caption=frame_text,
                                                  parse_mode='HTML')
                    case 2:
                        content = InputMediaVideo(media=frame['content'], caption=frame_text,
                                                  parse_mode='HTML')
                    case 3:
                        content = InputMediaAudio(media=frame['content'], caption=frame_text,
                                                  parse_mode='HTML')
                    case 4:
                        content = InputMediaAnimation(media=frame['content'], caption=frame_text, parse_mode='HTML')
                    case _:
                        content = None

                markup = InlineKeyboardBuilder()
                for key, value in frame['variants'].items():
                    markup.row(InlineKeyboardButton(text=value, callback_data=kb.FrameChange_CallbackData(frame_num=int(key)).pack()))
                if game['can_change_page']:
                    markup.row(InlineKeyboardButton(text=phr.change_page, callback_data=kb.ChangePageManual_CallbackData(game_code=game["game_code"]).pack()))
                if user['is_admin']:
                    markup.row(InlineKeyboardButton(text=phr.admin_info_frame, callback_data=kb.Admin_CallbackData(frame_num=int(frame['frame_num']), game_code=game['game_code']).pack()))
                markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game['game_code']).pack()))
                try:
                    if content is not None:
                        await call.message.edit_media(content, reply_markup=markup.as_markup())
                    else:
                        await call.message.edit_text(frame_text, reply_markup=markup.as_markup())
                except:
                    try:
                        await call.message.delete()
                    except:
                        pass

                    frame_text = frame['text']['ru']
                    if game['can_change_page']:
                        frame_text = f"{frame_text}\n\n" \
                                     f"Страница {frame['frame_num']} из {db.return_number_of_frames(game_code=game['game_code'])}"
                    match frame['content_code']:
                        case 1:
                            message = await call.message.answer_photo(frame['content'], caption=frame_text,
                                                                      reply_markup=markup.as_markup(), parse_mode='HTML')
                        case 2:
                            message = await call.message.answer_video(frame['content'], caption=frame_text,
                                                                      reply_markup=markup.as_markup(), parse_mode='HTML')
                        case 3:
                            message = await call.message.answer_audio(frame['content'], caption=frame_text,
                                                                      reply_markup=markup, parse_mode='HTML')
                        case 4:
                            message = await call.message.answer_animation(frame['content'], caption=frame_text,
                                                                          reply_markup=markup.as_markup(), parse_mode='HTML')
                        case _:
                            message = await call.message.answer(frame_text, reply_markup=markup.as_markup(),
                                                                parse_mode='HTML')

                    await state.update_data(game_text=message)
            else:
                try:
                    await call.message.delete()
                except:
                    pass
                await call.message.answer('На этом демо продукта заканчивается. Приобретите полную версию 💳')
            if frame['sound']:
                if data.get('sound') == None:
                    sound = await call.message.answer_audio(frame['sound'])
                    await state.update_data(sound=sound)
                    await state.update_data(sound_id=frame['sound'])
                else:
                    old_id = data.get('sound_id')
                    if old_id != frame['sound']:
                        await call.bot.delete_message(message_id=data.get('sound').message_id, chat_id=call.message.chat.id)
                        sound = await call.message.answer_audio(frame['sound'])
                        await state.update_data(sound=sound)
                        await state.update_data(sound_id=frame['sound'])


            if frame['achivement']:
                achiv = db.give_achivement_to_user(game_code=game['game_code'], achivement_code=frame['achivement'],
                                                   user_id=call.message.chat.id)
                if achiv != 0:
                    achivement = db.return_achivement(game_code=game['game_code'],
                                                      achivement_code=frame['achivement'])
                    ok = await call.message.answer(
                        text=f'Получено достижение ✅ {achivement["name"]}\nЧтобы посмотреть все достижения перейдите к меню достижений  📂')
                    await state.update_data(achivement=ok)

            if frame['change_add_conditions']:
                match frame['modificators']:
                    case 'str':
                        conditions = frame['change_add_conditions'].split('\n')
                        for i in conditions:
                            info = i.split(':')
                            key = info[0]
                            value = info[1]
                            db.update_user_game_config(call.message.chat.id, value, key, game['game_code'])
                    case 'int':
                        conditions = frame['change_add_conditions'].split('\n')
                        for i in conditions:
                            info = i.split(':')
                            key = info[0]
                            value = info[1]
                            cfg = db.return_game_cfg(user['user_id'], game['game_code'])
                            original_value = cfg[key]
                            expresion = f'{original_value}{value}'
                            res = s_log.integer_modificator(expresion)
                            db.update_user_game_config(call.message.chat.id, res, key, game['game_code'])

        elif frame == 0 and can_next == True:
            try:
                await call.message.edit_text(phr.end_of_product)
            except:
                try:
                    await call.message.delete()
                except:
                    pass
                await call.message.answer(phr.end_of_product)


@dp.callback_query(kb.FrameChange_CallbackData.filter())
async def change_frame_cb(call:types.CallbackQuery, callback_data: kb.FrameChange_CallbackData, state:FSMContext):
    await change_frames(call, int(callback_data.frame_num), state)

@dp.callback_query(kb.ChangePageManual_CallbackData.filter())
async def go_to_page(call:types.CallbackQuery, callback_data: kb.ChangePageManual_CallbackData, state:FSMContext):
    game_code = callback_data.game_code
    try:
        await call.message.edit_text(f'Напишите какую страницу вы желаете открыть?\nВ диапозоне от 1 до {db.return_number_of_frames(game_code)}\n\nОтправьте /cancel для отмены')
    except:
        await call.message.delete()
        await call.message.answer(f'Напишите какую страницу вы желаете открыть?\nВ диапозоне от 1 до {db.return_number_of_frames(game_code)}\n\nОтправьте /cancel для отмены')

    await state.set_state(Store.goto_page)


@dp.callback_query(kb.PlayingGame_CallbackData.filter())
async def start_play(call:types.CallbackQuery, callback_data: kb.PlayingGame_CallbackData, state:FSMContext):
    game = db.return_game_info(callback_data.game_code)
    user = db.return_user_info(call.message.chat.id)
    game_user_cfg = db.return_game_cfg(call.message.chat.id,game['game_code'])
    frame = db.return_frame(game_code=game['game_code'],frame_num=game_user_cfg['frame_num'])
    data = await state.get_data()
    try:
        await call.message.delete()
    except:
        await call.message.edit_text('Игра запущена')
    if frame != 0:
        db.user_played_game(user_id=call.message.chat.id, game_code=callback_data.game_code)
        if data.get('game_text'):
            try:
                await call.bot.delete_message(chat_id=call.message.chat.id,message_id=data.get('game_text').message_id)
            except:
                try:
                    await call.bot.edit_message_text(chat_id=call.message.chat.id,message_id=data.get('game_text').message_id, text='Сессия устарела \nЗапустите игру заново 🔁')
                except:
                    try:
                        await call.bot.edit_message_caption(chat_id=call.message.chat.id,message_id=data.get('game_text').message_id, caption='Сессия устарела \nЗапустите игру заново 🔁', reply_markup=None)
                    except:
                        pass
        db.update_now_user_game(call.message.chat.id,game['game_code'])
        frame_text = frame['text']['ru']
        if game['can_change_page']:
            frame_text = f"{frame_text}\n\n" \
                         f"Страница {frame['frame_num']} из {db.return_number_of_frames(game_code=game['game_code'])}"
        match frame['content_code']:
            case 1:
                content = InputMediaPhoto(media=frame['content'], caption=frame_text,parse_mode='HTML')
            case 2:
                content = InputMediaVideo(media=frame['content'], caption=frame_text,parse_mode='HTML')
            case 3:
                content = InputMediaAudio(media=frame['content'], caption=frame_text,parse_mode='HTML')
            case 4:
                content = InputMediaAnimation(media=frame['content'], caption=frame_text,parse_mode='HTML')
            case _:
                content = None

        markup = InlineKeyboardBuilder()
        for key, value in frame['variants'].items():
            markup.row(InlineKeyboardButton(text=value, callback_data=kb.FrameChange_CallbackData(frame_num=int(key)).pack()))
        if game['can_change_page']:
            markup.row(InlineKeyboardButton(text=phr.change_page, callback_data=kb.ChangePageManual_CallbackData(game_code=game["game_code"]).pack()))
        if user['is_admin']:
            markup.row(
                InlineKeyboardButton(text=phr.admin_info_frame, callback_data=kb.Admin_CallbackData(frame_num=int(frame['frame_num']), game_code=game['game_code']).pack()))
        markup.row(InlineKeyboardButton(text=phr.back_to_game, callback_data=kb.GetGameInfo_CallbackData(game_code=game['game_code']).pack()))
        try:
            await call.message.edit_media(content, reply_markup=markup.as_markup())
        except:
            try:
                await call.message.delete()
            except:
                pass
            frame_text = frame['text']['ru']
            if game['can_change_page']:
                frame_text = f"{frame_text}\n\n" \
                             f"Страница {frame['frame_num']} из {db.return_number_of_frames(game_code=game['game_code'])}"
            match frame['content_code']:
                case 1:
                    message = await call.message.answer_photo(frame['content'], caption=frame_text, reply_markup=markup.as_markup(), parse_mode='HTML', protect_content=True)
                case 2:
                    message = await call.message.answer_video(frame['content'], caption=frame_text,reply_markup=markup.as_markup(), parse_mode='HTML', protect_content=True)
                case 3:
                    message = await call.message.answer_audio(frame['content'], caption=frame_text,reply_markup=markup.as_markup(), parse_mode='HTML', protect_content=True)
                case 4:
                    message = await call.message.answer_animation(frame['content'], caption=frame_text,
                                                                  reply_markup=markup.as_markup(), parse_mode='HTML', protect_content=True)
                case _:
                    message = await call.message.answer(frame_text,reply_markup=markup.as_markup(), parse_mode='HTML', protect_content=True)
            await state.update_data(game_text=message)
        if frame['sound']:
            if data.get('sound') == None:
                sound = await call.message.answer_audio(frame['sound'])
                await state.update_data(sound=sound)
                await state.update_data(sound_id=frame['sound'])

            else:
                    old_id = data.get('sound_id')

                    if old_id != frame['sound']:
                        await call.bot.delete_message(message_id=data.get('sound').message_id,
                                                      chat_id=call.message.chat.id)
                        sound = await call.message.answer_audio(frame['sound'])
                        await state.update_data(sound=sound)
                        await state.update_data(sound_id=frame['sound'])
    else:
        await call.message.answer('У игры пока нет кадров. Но скоро это будет исправлено')
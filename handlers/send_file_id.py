from loader import dp,db
from aiogram import types, F


@dp.message(F.animation)
async def handle_gif(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_gif = message.animation.file_id
        await message.answer_video(id_gif,caption=id_gif)

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_photo = message.photo[-1].file_id
        await message.answer_photo(id_photo,caption=id_photo)
@dp.message(F.video)
async def handle_video(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_video = message.video.file_id
        await message.answer_video(id_video,caption=id_video)
@dp.message(F.sticker)
async def handle_sticker(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_sticker = message.sticker.file_id
        await message.answer_sticker(id_sticker)
        await message.answer(id_sticker)
@dp.message(F.audio)
async def handle_audio(message: types.Message):
    if db.return_user_info(message.from_user.id)['is_admin'] == 1:
        id_audio = message.audio.file_id
        await message.answer_audio(id_audio,caption=id_audio)

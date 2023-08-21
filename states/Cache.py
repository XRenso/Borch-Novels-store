from aiogram.dispatcher.filters.state import State, StatesGroup

class Cache(StatesGroup):
    sound = State()
    sound_id = State()
    game_text = State()
    achivement = State()
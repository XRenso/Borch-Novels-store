from aiogram.fsm.state import State, StatesGroup

class Store(StatesGroup):
    search_game = State()
    goto_page = State()
    create_user_group = State()
from aiogram.dispatcher.filters.state import State, StatesGroup

class Store(StatesGroup):
    search_game = State()
    goto_page = State()
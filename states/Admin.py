from aiogram.fsm.state import State, StatesGroup

class Admin(StatesGroup):
    send_message = State()
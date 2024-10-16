from aiogram.fsm.state import StatesGroup, State


class add_comment(StatesGroup):
    comment = State()
    progress = State()
    
    
    
class new_service(StatesGroup):
    chose = State()
    add_short = State()
    add_descr = State()
    add_critical = State()
    add_request = State()
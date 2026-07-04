from aiogram.fsm.state import State, StatesGroup

class ClientStates(StatesGroup):
    language = State()
    phone = State()
    main_menu = State()
    cart = State()
    location = State()
    payment_type = State()
    upload_check = State()

class AdminStates(StatesGroup):
    mailing = State()
    change_price = State()
    rejection_reason = State()
    check_rejection_reason = State()
    add_channel = State()
    edit_terms = State()
    add_image = State()

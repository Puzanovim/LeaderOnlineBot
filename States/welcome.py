from aiogram.dispatcher.filters.state import State, StatesGroup


class Welcome(StatesGroup):
    name = State()  # Will be represented in storage as 'Welcome:name'
    institute = State()  # Will be represented in storage as 'Welcome:institute'
    photo = State()  # Will be represented in storage as 'Welcome:photo'

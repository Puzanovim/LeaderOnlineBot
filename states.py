from aiogram.dispatcher.filters.state import State, StatesGroup


class Welcome(StatesGroup):
    name = State()  # Will be represented in storage as 'Welcome:name'
    institute = State()  # Will be represented in storage as 'Welcome:institute'
    photo = State()  # Will be represented in storage as 'Welcome:photo'


class ChangeName(StatesGroup):
    name = State()


class Quiz(StatesGroup):
    Task1 = State()
    Task2 = State()
    Task3 = State()
    Task4 = State()
    Task5 = State()
    Task6 = State()
    Task7 = State()
    Task8 = State()
    Task9 = State()
    Task10 = State()
    Task11 = State()
    Task12 = State()
    Task13 = State()
    Task14 = State()
    Task15 = State()
    Task16 = State()
    Task17 = State()
    Task18 = State()
    Task19 = State()
    Task20 = State()
    Task21 = State()
    Task22 = State()
    Task23 = State()
    Task24 = State()
    Task25 = State()
    Task26 = State()
    Task27 = State()
    Task28 = State()
    Task29 = State()
    Task30 = State()

from aiogram.dispatcher.filters.state import State, StatesGroup


class Quiz(StatesGroup):
    questions = []
    for i in range(30):
        question = State()
        questions.append(question)

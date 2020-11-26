from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton


from config import TOKEN
from messages import MESSAGES, questions, institutes
from states import Welcome, Quiz
from db import Db


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Db()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await Welcome.name.set()
    await message.reply(MESSAGES['start'], reply=False)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'], reply=False)


@dp.message_handler(commands=['result'])
async def result(message: types.Message):
    my_result = db.get_result(message.from_user.id)
    text = MESSAGES['result'] + str(my_result)
    await message.reply(text, reply=False)


@dp.message_handler(state=Welcome.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    db.create_user(message.from_user.id, message.text)
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for institut in institutes.keys():
        institut_btn = KeyboardButton(institut)
        markup.add(institut_btn)
    await Welcome.next()
    await message.reply(MESSAGES['institute'], reply_markup=markup, reply=False)


@dp.message_handler(state=Welcome.institute)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user institute
    """
    async with state.proxy() as data:
        data['institute'] = message.text

    # добавляем институт в БД
    db.add_institute(message.from_user.id, message.text)

    text = MESSAGES['course']
    for course in institutes[message.text]:
        text += course + "\n\n"
    await Welcome.next()
    await message.reply(text, reply=False)


@dp.message_handler(content_types=['photo'], state=Welcome.photo)
async def forward(message: types.Message, state: FSMContext):  # TODO проверить тип сообщения для фотографии
    """
    Process user registration
    """
    await state.finish()
    await message.reply(MESSAGES['photo'], reply=False)


@dp.message_handler(commands=['start_Quiz'])
async def start_quiz(message: types.Message):
    if db.get_current_question(user_id=message.from_user.id) > 30:
        text = MESSAGES['you are finished']
        markup = ReplyKeyboardRemove()
    else:
        await Quiz.Task1.set()
        db.increment_current_question(message.from_user.id, 0)
        text = questions[1]['Question']
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        for choice in questions[1]['Choices']:
            choice_btn = KeyboardButton(choice)
            markup.add(choice_btn)
    await message.reply(text, reply_markup=markup, reply=False)


@dp.message_handler(state=Quiz)
async def questions_step_by_step(message: types.Message, state: FSMContext):
    """
    Функция квиза
    # TODO разобраться со стейтами (используем / не используем)
    :param state:
    :param message: сообщение пользователя
    :return: отправляем следующий вопрос
    """
    user_id: int = message.from_user.id
    current_question: int = db.get_current_question(user_id)

    async with state.proxy() as data:
        data[current_question] = message.text

    right_answer = False
    if current_question > 30:
        text = MESSAGES['you are finished']
        markup = ReplyKeyboardRemove()
    else:
        question = questions[current_question]
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        user_answer = message.text.lower()
        true_answer = questions[current_question]['Answer'].lower()

        if user_answer == true_answer:
            right_answer = True
            db.set_point(user_id, current_question)

        have_hint = db.have_hints(user_id)
        if current_question + 1 > 20:
            markup = ReplyKeyboardRemove()
            #  here open questions
            if not right_answer and not have_hint:
                # даем подсказку
                text = MESSAGES['hint'] + question['Choices'][0]
                db.set_hint(user_id)
            else:
                # он дал верный ответ или уже была одна подсказка
                db.delete_hint(user_id)
                db.increment_current_question(user_id, current_question)
                if current_question == 30:
                    text = MESSAGES['the_end']
                    await state.finish()
                else:
                    question = questions[current_question + 1]
                    text = question['Question']
                    await Quiz.next()
        else:
            #  here quiz questions
            db.increment_current_question(user_id, current_question)
            question = questions[current_question + 1]
            text = question['Question']
            for choice in question['Choices']:
                choice_btn = KeyboardButton(choice)
                markup.add(choice_btn)
            await Quiz.next()
    await message.reply(text, reply_markup=markup, reply=False)


@dp.message_handler()
async def echo_message(message: types.Message):
    await message.reply(MESSAGES['unknown'], reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

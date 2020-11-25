from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
import asyncio


from config import TOKEN
from messages import MESSAGES
from States.welcome import Welcome
from States.quiz import Quiz
from db import Db
from dataQuiz import questions, institutes


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage)
db = Db()


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'], reply=False)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'], reply=False)


@dp.message_handler(commands=['get_my_result'])
async def result(message: types.Message):
    my_result = db.get_result(message.from_user.id)
    text = MESSAGES['result'] + str(my_result)
    await message.reply(text, reply_markup=False, reply=False)


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
        text += course + "\n"
    await Welcome.next()
    await message.reply(text, reply_markup=False, reply=False)


@dp.message_handler(content_types=['photo'], state=Welcome.photo)
async def forward(message: types.Message, state: FSMContext):  # TODO проверить тип сообщения для фотографии
    """
    Process user registration
    """
    await message.reply(MESSAGES['photo'], reply=False)


@dp.message_handler(state='*', commands=['start_Quiz'])
async def questions_step_by_step(message: types.Message, state: FSMContext):
    """
    Функция квиза
    # TODO разобраться со стейтами (используем / не используем)
    :param message: сообщение пользователя
    :return: отправляем следующий вопрос
    """
    user_id = message.from_user.id
    current_question = db.get_current_question(user_id)
    right_answer = False
    question = questions[current_question]
    markup = False

    if message.text == questions[current_question]['Answer']:
        right_answer = True
        db.set_point(user_id, questions)

    if current_question + 1 > 20:
        #  here open questions
        if not right_answer:
            # TODO счетчик подсказок
            # он дал не верный ответ, даем подсказку
            text = question['Choices'][0]
        else:
            # он дал верный ответ
            db.increment_current_question(user_id, current_question)
            question = questions[current_question + 1]
            text = question['Question']
    else:
        #  here quiz questions
        db.increment_current_question(user_id, current_question)
        question = questions[current_question + 1]
        text = question['Question']
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for choice in question['Choices']:
            choice_btn = KeyboardButton(choice)
            markup.add(choice_btn)
    await message.reply(text, reply_markup=markup, reply=False)


@dp.message_handler()
async def echo_message(message: types.Message):
    await message.reply(MESSAGES['unknown'], reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

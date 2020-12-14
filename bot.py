from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from PIL import Image, ImageDraw, ImageFont
from asyncio import sleep

from config import TOKEN
from messages import MESSAGES, questions, institutes
from states import Welcome, Quiz, ChangeName
from db import Db

from glob import glob
from random import choice

# image8 = "https://drive.google.com/drive/folders/1WFZ1RyGLB-Qe7wenvy7KtUK92Lm7g84P"


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
db = Db()


@dp.message_handler(commands=['h'])
async def send_cert(message: types.Message):
    await message.reply(MESSAGES['alert_change_name'], reply=False)


@dp.message_handler(commands=['get_gifts_all'])
async def send_cert(message: types.Message):
    users = db.get_users()
    for user in users:
        try:
            name = user['name']
            user_id = user['user_id']

            image = Image.open("./certs/cert.png")
            draw = ImageDraw.Draw(image)

            W = 2480
            style = ImageFont.truetype('11528.ttf', size=120)

            w, h = style.getsize(name)
            draw.text(((W-w)/2, 1550), name, font=style, fill="#fff")

            name_cert = name + ".png"
            image.save(name_cert, "PNG")

            text = MESSAGES['gift']
            img = name_cert
            await bot.send_photo(user_id, photo=open(img, 'rb'), caption=text)
            print(f"Gift to {name} with id={user_id} sent!")
            await sleep(1)
        except Exception as e:
            print(e)


@dp.message_handler(commands=['get_name_alert_all'])
async def send_cert(message: types.Message):
    users = db.get_users()
    for user in users:
        try:
            name = user['name']
            user_id = user['user_id']
            text = MESSAGES['alert_change_name'] + name
            await bot.send_message(user_id, text)
            print(f"Alert to {name} with id={user_id} sent!")
            await sleep(1)
        except Exception as e:
            print(e)


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
    images = glob("img/*")
    img = choice(images)
    await bot.send_photo(message.from_user.id, photo=open(img, 'rb'), caption=text)


@dp.message_handler(commands=['change_name'])
async def change_name(message: types.Message):
    await ChangeName.name.set()
    await message.reply(MESSAGES["change_name"], reply=False)


@dp.message_handler(state=ChangeName.name)
async def set_name(message: types.Message, state: FSMContext):
    """
    Change user name
    """
    if message.text == "N":
        text = MESSAGES["old_name"] + db.get_name(message.from_user.id) + MESSAGES["change_name_again"]
    else:
        answer = db.update_name(message.from_user.id, message.text)
        if answer == 1:
            text = MESSAGES["new_name"] + message.text + MESSAGES["change_name_again"]
        else:
            text = MESSAGES["repeat_name"]
    await state.finish()
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
async def process_institute(message: types.Message, state: FSMContext):
    """
    Process user institute
    """
    async with state.proxy() as data:
        data['institute'] = message.text

    # добавляем институт в БД
    db.add_institute(message.from_user.id, message.text)

    # text = MESSAGES['course']
    # for course in institutes["я не из УрФУ"]:
    #     text += course + "\n\n"

    text = MESSAGES['course']
    for course in institutes[message.text]:
        text += course + "\n\n"
    await Welcome.next()
    await message.reply(text, reply=False)


@dp.message_handler(content_types=['photo'], state=Welcome.photo)
async def process_photo(message: types.Message, state: FSMContext):
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
    if message.text in MESSAGES.keys():
        text = MESSAGES[message.text]
    else:
        text = MESSAGES['unknown']
    await message.reply(text, reply=False)


executor.start_polling(dp, skip_updates=True)

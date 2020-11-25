from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import asyncio


from config import TOKEN
from messages import MESSAGES
from States.welcome import Welcome
from States.quiz import Quiz


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(MESSAGES['start'], reply=False)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'], reply=False)


@dp.message_handler(state=Welcome.name)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user name
    """
    async with state.proxy() as data:
        data['name'] = message.text

    # TODO запись имени в бд
    # TODO добавить клавиатуру специальностей
    await Welcome.next()
    await message.reply(MESSAGES['institute'], reply=False)


@dp.message_handler(state=Welcome.institute)
async def process_name(message: types.Message, state: FSMContext):
    """
    Process user institute
    """
    async with state.proxy() as data:
        data['institute'] = message.text
    # TODO обработка сообдения по институту
    # TODO запись института в бд
    # TODO убрать клавиатуру
    await Welcome.next()
    await message.reply(MESSAGES['course'], reply=False)


@dp.message_handler(content_types=['photo'], state=Welcome.photo)
async def forward(message: types.Message, state: FSMContext):  # TODO проверить тип сообщения для фотографии
    """
    Process user registration
    """
    # await bot.forward_message(msg.from_user.id, msg.from_user.id, msg.message_id)
    await message.reply(MESSAGES['photo'], reply=False)


@dp.message_handler(state='*', commands=['startQuiz'])
async def process_help_command(message: types.Message, state: FSMContext):
    """
    # TODO get current question by user_id
    # TODO get answer by current question and compare with message
    # TODO update data coin for current question and current_question++ in db
    # TODO get data question for current question + 1
    # TODO if list answers is empty, not use the keyboard
    # TODO create text (and keyboard) for question + 1
    :param message:
    :return:
    """
    await message.reply(MESSAGES['help'], reply=False)


@dp.message_handler()
async def echo_message(message: types.Message):
    await message.reply(MESSAGES['unknown'], reply=False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

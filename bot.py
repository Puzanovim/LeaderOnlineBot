from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
import asyncio


from config import TOKEN, ADMIN
from messages import MESSAGES
from States.welcome import Welcome


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
    await message.reply(MESSAGES['institute'])


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
    await message.reply(MESSAGES['course'])


@dp.message_handler(content_types=['photo'], state=Welcome.photo)
async def forward(msg: types.Message):  # TODO проверить тип сообщения для фотографии
    """
    Process user registration
    """
    # await bot.forward_message(msg.from_user.id, msg.from_user.id, msg.message_id)
    await asyncio.sleep(5)
    word = "Спасибо за отправленное фото"
    await bot.send_message(msg.from_user.id, word)


@dp.message_handler()
async def echo_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

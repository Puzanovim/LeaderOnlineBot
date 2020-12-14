# from aiogram import Bot
# from aiogram.dispatcher import Dispatcher
# from aiogram.utils import executor
#
# from PIL import Image, ImageDraw, ImageFont
# from db import Db
#
# from config import TOKEN
# from messages import MESSAGES
#
# bot = Bot(token=TOKEN)
# dp = Dispatcher(bot)
# db = Db()
#
#
# async def send_cert():
#     users = db.get_users()
#     for user in users:
#         name = user['name']
#         user_id = user['user_id']
#
#         image = Image.open("cert.png")
#         draw = ImageDraw.Draw(image)
#
#         W = 2480
#         style = ImageFont.truetype('11528.ttf', size=120)
#
#         w, h = style.getsize(name)
#         draw.text(((W-w)/2, 1550), name, font=style, fill="#fff")
#
#         name_cert = name + ".png"
#         image.save(name_cert, "PNG")
#
#         text = MESSAGES['gift']
#         img = name_cert
#         await bot.send_photo(user_id, photo=open(img, 'rb'), caption=text)
#         print(f"Gift to {name} with id={user_id} sent!")


# image = Image.open("cert.png")
# draw = ImageDraw.Draw(image)
#
# W = 2480
# style = ImageFont.truetype('11528.ttf', size=120)
# name = "Пузанов Игорь Михайлович"
#
# w, h = style.getsize(name)
# draw.text(((W-w)/2, 1550), name, font=style, fill="#fff")
#
# name_cert = name + ".png"
# image.save(name_cert, "PNG")

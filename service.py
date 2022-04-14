import db as database
import config as cfg
from aiogram import types

db = database.Database()


def is_admin(func):
    """
    Checking user for admin privileges
    """
    async def wrapper(message: types.Message):
        admins_list = await cfg.bot.get_chat_administrators(message.chat.id)
        if int(message.from_user.id) in [x["user"]["id"] for x in admins_list]:
            return await func(message)
    return wrapper


def is_owner(func):
    async def wrapper(message: types.Message):
        if int(message.from_user.id) == cfg.ADMIN_ID:
            return await func(message)
    return wrapper

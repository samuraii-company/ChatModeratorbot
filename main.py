import config as cfg

import db as database
import logging
from aiogram import types
from aiogram.utils import executor
from service import is_admin, is_owner
import time
from aiogram.utils import exceptions as ex
    
db = database.Database()
logging.basicConfig(level=logging.INFO)


@cfg.dp.message_handler(commands="mute")
@is_admin
async def mute_user(message: types.Message):
    """
    Command for mute user
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return

    await cfg.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=message.reply_to_message.from_user.id,
        permissions={"can_send_messages": False},
        until_date=int(time.time()) + 60 * 10
    )
    await message.bot.delete_message(message.chat.id, message.message_id)
    await message.reply_to_message.reply("Пользователь был замучен на 10 минут!!!")


@cfg.dp.message_handler(commands="allmute")
@is_admin
async def mute_all_user(message: types.Message):
    """
    Command for mute all users
    """
    await cfg.bot.set_chat_permissions(chat_id=message.chat.id, permissions={"can_send_messages": False})
    await message.answer("Включен полный мут чата")


@cfg.dp.message_handler(commands="allunmute")
@is_admin
async def unmute_all_user(message: types.Message):
    """
    Command for unmute all users
    """
    await cfg.bot.set_chat_permissions(chat_id=message.chat.id, permissions={"can_send_messages": True})
    await message.answer("Полный мут чата выключен")


@cfg.dp.message_handler(commands="ban")
@is_admin
async def ban_user(message: types.Message):
    """
    Command for ban user
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return

    try:
        await cfg.bot.ban_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
        await message.bot.delete_message(message.chat.id, message.message_id)
        await message.reply_to_message.reply("Пользователь был забанен!!!")
    except (ex.CantRestrictSelf, ex.CantRestrictChatOwner, ex.UserIsAnAdministratorOfTheChat):
        await message.answer("Невозможно выполнить эту команду для этого пользователя")


@cfg.dp.message_handler(commands="unban")
@is_admin
async def unban_user(message: types.Message):
    """
    Command for unban user
    """
    admins_list = await cfg.bot.get_chat_administrators(message.chat.id)
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return

    if int(message.reply_to_message.from_user.id) in [x["user"]["id"] for x in admins_list]:
        await message.answer("Невозможно выполнить эту команду для этого пользователя")
    else:
        await cfg.bot.unban_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
        await message.bot.delete_message(message.chat.id, message.message_id)
        await message.reply_to_message.reply("Пользователь был разбанен!!!")


@cfg.dp.message_handler(commands="sendall")
@is_owner
async def create_spam(message: types.Message):
    """
    Create Spam Message
    """
    if not message.reply_to_message or not message.chat.type == "private":
        await message.answer("Эта команда должна быть ответом на сообщение В приватном чате с ботом")
        return

    _user_list = (x["user_id"] async for x in await db.get_all())
    async for user in _user_list:
        try:
            await message.reply_to_message.copy_to(user)
        except ex.BotBlocked:
            await db.update_one(user_id=user, key="status", value=False)


@cfg.dp.message_handler(content_types="text")
async def words_filter(message: types.Message):
    """
    Filtering message text, for ban words
    """
    for word in cfg.BAD_WORDS:
        if word in message.text.lower():
            await message.delete()
            break


@cfg.dp.message_handler(content_types=["new_chat_members"])
async def new_chat_member(message: types.Message):
    """
    Welcoming new caht members
    """
    _username = message.from_user.username if message.from_user.username else "пользователя"
    await message.answer(f"Поприветствуем {_username} в чате")

    if not await db.exists(message.from_user.id):
        _user_id = int(message.from_user.id)
        _username = message.from_user.username

        await db.insert_one({"user_id": _user_id, "username": _username, "status": True})


if __name__ == "__main__":
    executor.start_polling(cfg.dp, loop=cfg.loop, skip_updates=True)

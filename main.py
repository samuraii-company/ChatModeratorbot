import config as cfg

import db as database
import logging
from aiogram import types
from aiogram.utils import executor
from service import only_chat_admin, mute_unmute_commands, restrict_user
from banwords import BAN_WORDS
import time
from aiogram.utils import exceptions as ex
import button as btn
from aiogram.dispatcher import FSMContext
    
db = database.Database()
logging.basicConfig(level=logging.INFO)


@cfg.dp.message_handler(commands="mute")
@only_chat_admin
async def mute_user(message: types.Message):
    """
    Command for mute user
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return
    await mute_unmute_commands(
        permission=False,
        text_message="Пользователь был замучен на 10 минут!!!",
        message=message,
        mute_time=int(time.time()) + 60 * 10
    )
        
        
@cfg.dp.message_handler(commands="unmute")
@only_chat_admin
async def mute_user(message: types.Message):
    """
    Command for mute user
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return
    await mute_unmute_commands(
        permission=True,
        text_message="Пользователь был размучен",
        message=message,
        mute_time=0
    )


@cfg.dp.message_handler(commands="allmute")
@only_chat_admin
async def mute_all_user(message: types.Message):
    """
    Command for mute all users
    """
    await cfg.bot.set_chat_permissions(chat_id=message.chat.id, permissions={"can_send_messages": False})
    await message.answer("Включен полный мут чата")


@cfg.dp.message_handler(commands="allunmute")
@only_chat_admin
async def unmute_all_user(message: types.Message):
    """
    Command for unmute all users
    """
    await cfg.bot.set_chat_permissions(chat_id=message.chat.id, permissions={"can_send_messages": True})
    await message.answer("Полный мут чата выключен")


@cfg.dp.message_handler(commands="ban")
@only_chat_admin
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
@only_chat_admin
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


@cfg.dp.message_handler(content_types="text")
async def words_filter(message: types.Message):
    """
    Filtering message text, for ban words
    """
    for word in BAN_WORDS:
        if word in message.text.lower():
            await message.delete()
            break


@cfg.dp.message_handler(content_types=["new_chat_members"])
async def new_chat_member(message: types.Message):
    """
    Welcoming new caht members
    """
    await restrict_user(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        permission=False,
        mute_time=int(time.time()) * 60 * 600
    )
    await message.answer("Подтвердите, что вы человек", reply_markup=btn.captcha_markup)
    await cfg.Message_State.accept_user.set()


@cfg.dp.callback_query_handler(text="not_robot", state=cfg.Message_State.accept_user)
async def accept_captcha(request: types.CallbackQuery, state: FSMContext):
    """
    Accept Captcha Button
    """
    await state.finish()
    await request.bot.delete_message(
        request.message.chat.id,
        request.message.message_id
    )
    await restrict_user(
        chat_id=request.message.chat.id,
        user_id=request.from_user.id,
        permission=True,
        mute_time=0
    )

    _username = request.from_user.username if request.from_user.username else "пользователя"
    await request.bot.send_message(request.message.chat.id, f"Поприветствуем {_username} в чате")


if __name__ == "__main__":
    executor.start_polling(cfg.dp, loop=cfg.loop, skip_updates=True)

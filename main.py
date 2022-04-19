import config as cfg
import db as database
import logging

from aiogram import types
from aiogram.utils import executor
from aiogram.utils import exceptions as ex
from aiogram.dispatcher import FSMContext

from service import (
    is_owner,
    only_chat_admin,
    mute_unmute_commands,
    restrict_user
)

from banwords import BAN_WORDS
from filters import PrivateChat, GroupChat
import time
import button as btn
import messages as msg

cfg.dp.filters_factory.bind(PrivateChat)
cfg.dp.filters_factory.bind(GroupChat)

logging.basicConfig(level=logging.INFO)


@cfg.dp.message_handler(private_chat=True, commands="start")
async def start_command(message: types.Message):
    """
    Start Command
    """
    db = database.PrivateUserDatabase()
    if not await db.exists(message.from_user.id):
        await db.insert_one({
            "user_id": int(message.from_user.id),
            "username": message.from_user.username,
       })
    await cfg.bot.send_message(message.from_user.id, msg.start_message, reply_markup=btn.instruciton_markup)


@cfg.dp.message_handler(private_chat=True, commands="info")
async def info_command(message: types.Message):
    """
    Info Command
    """
    await cfg.bot.send_message(message.from_user.id, msg.info_message)


@cfg.dp.message_handler(private_chat=True, commands="quastion")
async def quastion_command(message: types.Message):
    """
    Quastion Command
    """
    await cfg.bot.send_message(message.from_user.id, "Отправьте сообщение, которое вы хотите отправить администрации")
    await cfg.UserState.quastion.set()


@cfg.dp.message_handler(state=cfg.UserState.quastion)
async def quastion_callback(message: types.Message, state: FSMContext):
    """
    Quastion Callback
    """
    await message.forward(cfg.OWNER_ID)
    await message.answer("Сообщение успешно отправлено")
    await message.bot.send_message(cfg.OWNER_ID, f"Сообщение от пользователя {message.from_user.id}")
    
    await state.finish()


@cfg.dp.message_handler(group_chat=True, commands="rules")
async def get_rules(message: types.Message):
    """
    Get Rules by chat command
    """
    db = database.Rules()
    if not await db.exists(chat_id=message.chat.id):
        await message.answer("Для данного чата правила еще не установлены")
    else:
        rules = await db.get_rules(chat_id=message.chat.id)
        await message.answer(rules["rules"])


@cfg.dp.message_handler(group_chat=True, commands="setrules")
@only_chat_admin
async def set_rules_command(message: types.Message):
    """
    Set Rules by chat command
    """
    await message.answer("Отправьте мне, список правил для данного чата")
    await cfg.RuleState.rules.set()
    

@cfg.dp.message_handler(state=cfg.RuleState.rules, content_types="text")
async def set_rules_state(message: types.Message, state: FSMContext):
    """
    Set Rules by chat state
    """
    db = database.Rules()
    if await db.exists(message.chat.id):
        await message.answer("Правила для данной группы уже существуют,чтобы удалить /deleterules")
    else:
        try:
            await db.set_rules(rules_data={"chat_id": message.chat.id, "rules": message.text})
            await message.answer("Правила успешно записаны")
        except Exception:
            await message.answer("Что-то пошло не так, попробуйте позже")
    await state.finish()
    
    
@cfg.dp.message_handler(commands="deleterules", group_chat=True)
@only_chat_admin
async def delete_rules(message: types.Message):
    """
    Delete rules by chat
    """
    db = database.Rules()
    if not await db.exists(message.chat.id):
        await message.answer("Правил для данной группы нет, чтобы создать /setrules")
    else:
        await db.delete_rules(chat_id=message.chat.id)
        await message.answer("Правила удалены")
    

@cfg.dp.message_handler(commands="report", group_chat=True)
async def report_user(message: types.Message):
    """
    Report command
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return

    db = database.UserDatabase()
    _user_id = message.reply_to_message.from_user.id
    if await db.exists(user_id=_user_id):
        _report_count = await db.report_count(user_id=_user_id)
    
        if not _report_count >= cfg.MAX_REPORTS_COUNT:
            await db.update_one(user_id=_user_id, key="reports", value=_report_count + 1)
            await message.answer("Ваша жалоба отправлена")
        else:
            admins_list = await cfg.bot.get_chat_administrators(message.chat.id)
            admins = [f"@{x['user']['username']}" for x in admins_list if x["status"] == "administrator" and \
            x["user"]["is_bot"] is False]
            await message.answer(",".join(admins) + "\n" + msg.reports_count_message)
    else:
        await db.insert_one({
            "user_id": message.reply_to_message.from_user.id,
            "username": message.reply_to_message.from_user.username,
            "chat_id": message.chat.id,
            "chat_title": message.chat.title,
            "chat_username": message.chat.username,
            "reports": 1
       })
        await message.answer("Ваша жалоба отправлена")


@cfg.dp.message_handler(commands="donation", private_chat=True)
async def donation_command(message: types.Message):
    """
    Donation command
    """
    await message.bot.send_animation(
        chat_id=message.from_user.id,
        animation=cfg.DONATION_GIF,
        reply_markup=btn.donation_markup
    )


@cfg.dp.message_handler(commands="justify", group_chat=True)
@only_chat_admin
async def justify_user(message: types.Message):
    """
    Justify user command
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return
    db = database.UserDatabase()
    _user_id = message.reply_to_message.from_user.id
    _report_count = await db.report_count(user_id=_user_id)
    if _report_count != 0:
        await db.update_one(user_id=_user_id, key="reports", value=0)
        await message.answer("Счетчик репортов сброшен")
    else:
        await message.answer("За пользователем нет грехов")
        

@cfg.dp.message_handler(private_chat=True, commands="admin", content_types=["text"])
@is_owner
async def admin_command(message: types.Message):
    """
    Admin Command
    """
    await cfg.bot.send_message(message.from_user.id, "С возвращением сэр", reply_markup=btn.admin_markup)


@cfg.dp.callback_query_handler(text="answer")
async def answer_button(request: types.CallbackQuery):
    """
    Answer Button
    """
    await request.message.edit_text("Введите id пользователя, которому вы  хотите ответить")
    await cfg.UserState.answer_id.set()


@cfg.dp.callback_query_handler(text="spam")
async def spam_button(request: types.CallbackQuery):
    """
    Spam Button
    """
    await request.message.edit_text(msg.spam_message)
    await cfg.SpamState.spam.set()
    

@cfg.dp.message_handler(state=cfg.SpamState.spam, content_types=types.ContentTypes.ANY)
async def create_spam(message: types.Message, state: FSMContext):
    """
    Create spam by all users
    """
    db = database.PrivateUserDatabase()
    async for user in (user["user_id"] async for user in await db.get_all()):
        try:
            await message.copy_to(user)
        except ex.BotBlocked:
            await db.delete_one(user_id=user)
    await message.answer("Рассылка завершена")
    await state.finish()


@cfg.dp.message_handler(state=cfg.UserState.answer_id, content_types='text')
async def answer_id_callback(message: types.Message, state: FSMContext):
    """
    Answer id Callback
    """
    if message.text.isnumeric():
        await state.update_data(answer_id=int(message.text))
        await message.answer("Введите ваш ответ на вопрос")
        await cfg.UserState.answer.set()
    else:
        await message.answer("Неверный id пользователя, попробуйте снова")
        await state.reset_state()


@cfg.dp.message_handler(state=cfg.UserState.answer, content_types='text')
async def answer_callback(message: types.Message, state: FSMContext):
    """
    Answer message Callback
    """
    _answer_id = await state.get_data()
    await message.bot.send_message(_answer_id["answer_id"], message.text)
    await message.answer("Ответ успешно отправлен")
    await state.finish()


@cfg.dp.message_handler(group_chat=True, commands="mute")
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
        

@cfg.dp.message_handler(group_chat=True, commands="unmute")
@only_chat_admin
async def unmute_user(message: types.Message):
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


@cfg.dp.message_handler(group_chat=True, commands="allmute")
@only_chat_admin
async def mute_all_user(message: types.Message):
    """
    Command for mute all users
    """
    await cfg.bot.set_chat_permissions(
        chat_id=message.chat.id,
        permissions={"can_send_messages": False, "can_send_other_messages": False}
    )
    await message.answer("Включен полный мут чата")


@cfg.dp.message_handler(group_chat=True, commands="allunmute")
@only_chat_admin
async def unmute_all_user(message: types.Message):
    """
    Command for unmute all users
    """
    await cfg.bot.set_chat_permissions(
        chat_id=message.chat.id,
        permissions={"can_send_messages": True, "can_send_other_messages": True}
    )
    await message.answer("Полный мут чата выключен")


@cfg.dp.message_handler(group_chat=True, commands="ban")
@only_chat_admin
async def ban_user(message: types.Message):
    """
    Command for ban user
    """
    if not message.reply_to_message:
        await message.answer("Эта команда должна быть ответом на сообщение")
        return
    try:
        db = database.UserDatabase()
        await cfg.bot.ban_chat_member(chat_id=message.chat.id, user_id=message.reply_to_message.from_user.id)
        await message.bot.delete_message(message.chat.id, message.message_id)
        await message.reply_to_message.reply("Пользователь был забанен!!!")
    
        await db.delete_one(user_id=message.reply_to_message.from_user.id)
    except (ex.CantRestrictSelf, ex.CantRestrictChatOwner, ex.UserIsAnAdministratorOfTheChat):
        await message.answer("Невозможно выполнить эту команду для этого пользователя")


@cfg.dp.message_handler(group_chat=True, commands="unban")
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


@cfg.dp.message_handler(group_chat=True, content_types="text")
async def words_filter(message: types.Message):
    """
    Filtering message text, for ban words
    """
    for word in BAN_WORDS:
        if word in message.text.lower():
            await message.delete()
            break


@cfg.dp.message_handler(group_chat=True, content_types=["left_chat_member"])
async def goodbuy_message(message: types.Message):
    await cfg.bot.send_message(message.chat.id, "Прощай, нам будет тебя нехватать")


@cfg.dp.message_handler(group_chat=True, content_types=["new_chat_members"])
async def new_chat_member(message: types.Message):
    """
    Welcoming new chat members
    """
    await restrict_user(
        chat_id=message.chat.id,
        user_id=message.from_user.id,
        permission=False,
        mute_time=int(time.time()) * 60 * 600
    )
    await message.answer("Подтвердите, что вы человек", reply_markup=btn.captcha_markup)
    await cfg.UserState.accept_user.set()


@cfg.dp.callback_query_handler(text="not_robot", state=cfg.UserState.accept_user)
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
    db = database.UserDatabase()
    if not await db.exists(request.from_user.id):
        await db.insert_one({
            "user_id": request.from_user.id,
            "username": request.from_user.username,
            "chat_id": request.message.chat.id,
            "chat_title": request.message.chat.title,
            "chat_username": request.message.chat.username,
            "reports": 0
       })


if __name__ == "__main__":
    executor.start_polling(cfg.dp, loop=cfg.loop, skip_updates=True)

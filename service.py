import config as cfg
from aiogram import types
from aiogram.utils import exceptions as ex
import csv
import os
from io import BytesIO
from datetime import datetime
from types import AsyncGeneratorType


def only_chat_admin(func):
    """
    Checking user for admin privileges
    """
    async def wrapper(message: types.Message):
        admins_list = await cfg.bot.get_chat_administrators(message.chat.id)
        if int(message.from_user.id) in [x["user"]["id"] for x in admins_list]:
            return await func(message)
    return wrapper


def is_owner(func):
    """Checking user for owner privileges"""
    async def wrapper(message: types.Message):
        if int(message.from_user.id) == cfg.OWNER_ID:
            return await func(message)
    return wrapper


async def mute_unmute_commands(permission: bool, message: types.Message, text_message: str, mute_time: int):
    """Mute, Unmute Commands Callback"""
    try:
        await restrict_user(
            chat_id=message.chat.id,
            user_id=message.reply_to_message.from_user.id,
            permission=permission,
            mute_time=mute_time
        )
        await message.bot.delete_message(message.chat.id, message.message_id)
        await message.reply_to_message.reply(text_message)
    except (ex.CantRestrictSelf, ex.CantRestrictChatOwner, ex.UserIsAnAdministratorOfTheChat):
        await message.answer("Невозможно выполнить эту команду для этого пользователя")


async def restrict_user(chat_id: int, user_id: int, permission: bool, mute_time: int) -> None:
    """
    Restrict User Permission to send Message on chat
    """
    await cfg.bot.restrict_chat_member(
        chat_id=chat_id,
        user_id=user_id,
        permissions={
            "can_send_messages": permission,
            "can_send_other_messages": permission,
        },
        until_date=mute_time
    )


class Statistics:
    """
    Users List Excel
    """
    def __init__(self):
        self.filename = f"Статистика{str(datetime.date)}"
        self.row = ["ID", "Username", "Chat_id", "Chat_title", "Chat_username"]
        
    async def create(self) -> None:
        with open(f"{self.filename}.csv", "w", encoding="utf-8") as f:
            writter = csv.writer(f, delimiter=",", lineterminator="\r")
            writter.writerow(self.row)
        
    async def append(self, user_row) -> None:
        with open(f"{self.filename}.csv", "a") as f:
            writter = csv.writer(f)
            writter.writerow(
                [
                user_row["user_id"],
                user_row["username"],
                user_row["chat_id"],
                user_row["chat_title"],
                user_row["chat_username"],
                ]
            )

    async def prepare(self, data: AsyncGeneratorType) -> None:
        """
        Preparing data for writing in file
        """
        await self.create()
        [await self.append(row) async for row in data]

    async def getfile(self) -> BytesIO:
        with open(f"{self.filename}.csv", "rb") as f:
            csv_file = BytesIO(f.read())
            csv_file.name = f'{self.filename}.csv'
            return csv_file
        
    async def delete(self) -> None:
        os.remove(f"{self.filename}.csv")

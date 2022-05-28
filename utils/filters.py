from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class PrivateChat(BoundFilter):
    key = "private_chat"

    def __init__(self, private_chat):
        self.private_chat = private_chat

    async def check(self, message: types.Message) -> bool:
        if message.chat.type == "private":
            return True
        return False


class GroupChat(BoundFilter):
    key = "group_chat"

    def __init__(self, group_chat):
        self.group_chat = group_chat

    async def check(self, message: types.Message) -> bool:
        if message.chat.type != "private":
            return True
        return False

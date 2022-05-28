import time
from config import config as cfg
from aiogram import types
from aiogram.utils import exceptions as ex
from utils.structs import MuteStruct, UserStrictStruct
from utils.search import admin_search


def only_chat_admin(func):
    """
    Checking user for admin privileges
    """

    async def wrapper(message: types.Message):
        admins_list = [
            admin["user"]["id"]
            for admin in await cfg.bot.get_chat_administrators(message.chat.id)
        ]

        _status = await admin_search(admins_list, int(message.from_user.id))

        if _status:
            return await func(message)

    return wrapper


def is_owner(func):
    """Checking user for owner privileges"""

    async def wrapper(message: types.Message):
        if int(message.from_user.id) == cfg.OWNER_ID:
            return await func(message)

    return wrapper


async def _restrict_user(payload: UserStrictStruct) -> None:
    """Restrict user permission in chat"""

    await cfg.bot.restrict_chat_member(
        chat_id=payload.chat_id,
        user_id=payload.user_id,
        permissions={
            "can_send_messages": payload.permissions,
            "can_send_other_messages": payload.permissions,
        },
        until_date=payload.until_date,
    )


class CaptchaFunction:
    """Captcha Functional"""

    def __init__(self, payload: UserStrictStruct):
        self.payload = payload

    @classmethod
    async def init_captcha(cls, message: types.Message) -> "CaptchaFunction":
        """Init instance with init captcha configuration"""

        LONG_MUTE_TIME = int(time.time()) * 60 * 600
        return cls(
            UserStrictStruct(
                permissions=False,
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                until_date=LONG_MUTE_TIME,
            )
        )

    @classmethod
    async def accept_captcha(cls, request: types.CallbackQuery) -> "CaptchaFunction":
        """Init instance with accept captcha configuration"""

        return cls(
            UserStrictStruct(
                permissions=True,
                chat_id=request.message.chat.id,
                user_id=request.from_user.id,
                until_date=0,
            )
        )

    async def apply(self):
        """Applying captcha function"""

        await _restrict_user(self.payload)


class MuteChatFunction:
    """Restricting user Permission in chat"""

    def __init__(self, payload: MuteStruct):
        self.payload = payload

    @classmethod
    async def mute_init(cls, message: types.Message) -> "MuteChatFunction":
        """Init instance with mute configutaion"""

        MUTE_TIME = int(time.time()) * 60 * 10
        return cls(
            MuteStruct(
                permission=False,
                text_message="Пользователь был замучен на 10 минут!!!",
                message=message,
                mute_time=MUTE_TIME,
            )
        )

    @classmethod
    async def unmute_init(cls, message: types.Message) -> "MuteChatFunction":
        """Init instance with unmute configutaion"""

        return cls(
            MuteStruct(
                permission=True,
                text_message="Пользователь был размучен",
                message=message,
                mute_time=0,
            )
        )

    async def apply(self):
        """Applying user permission in chat"""

        try:
            await _restrict_user(
                UserStrictStruct(
                    chat_id=self.payload.message.chat.id,
                    user_id=self.payload.message.reply_to_message.from_user.id,
                    permissions=self.payload.permission,
                    until_date=self.payload.mute_time,
                )
            )
            await self.payload.message.bot.delete_message(
                self.payload.message.chat.id, self.payload.message.message_id
            )
            await self.payload.message.reply_to_message.reply(self.payload.text_message)

        except (
            ex.CantRestrictSelf,
            ex.CantRestrictChatOwner,
            ex.UserIsAnAdministratorOfTheChat,
        ):
            await self.payload.message.answer(
                "Невозможно выполнить эту команду для этого пользователя"
            )

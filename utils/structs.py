from aiogram import types
from dataclasses import dataclass


@dataclass
class CollectionName:
    """MongoDB collections names"""

    users: str = "chat_users"
    private_users: str = "private_users"


@dataclass
class NewPrivateUserStruct:
    """New Private User Info Struct"""

    user_id: int
    username: str


@dataclass
class NewUserStruct:
    """New User Info Struct"""
   
    user_id: int
    username: str
    chat_id: int
    chat_title: str
    chat_username: str


@dataclass
class RulesInfo:
    """Struct of rules data"""

    chat_id: int
    rules: str


@dataclass
class MuteStruct:
    """Struct of mute or unmute data"""

    permission: bool
    text_message: str
    message: types.Message
    mute_time: int


@dataclass
class UserStrictStruct:
    """Struct of user strict data in chat"""

    chat_id: int
    user_id: int
    permissions: bool
    until_date: int

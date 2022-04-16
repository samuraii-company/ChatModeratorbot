import asyncio
from dotenv import load_dotenv
import os
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

load_dotenv()

TOKEN: str = os.getenv("TOKEN")
OWNER_ID: int = int(os.getenv("OWNER_ID"))

MAX_REPORTS_COUNT = 3

loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    accept_user = State()
    quastion = State()
    answer_id = State()
    answer = State()


class SpamState(StatesGroup):
    spam = State()


class RuleState(StatesGroup):
    rules = State()

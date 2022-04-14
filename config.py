import asyncio
from dotenv import load_dotenv
import os
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher

load_dotenv()

TOKEN: str = os.getenv("TOKEN")
ADMIN_ID: int = int(os.getenv("ADMIN_ID"))

loop = asyncio.get_event_loop()
bot = Bot(TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())


class Message_State(StatesGroup):
    accept_user = State()

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


captcha_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Я человек", callback_data="not_robot")
)

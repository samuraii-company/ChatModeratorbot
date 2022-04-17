from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


DONATION_URL = "https://inlnk.ru/KenDJa"

INSTRUCTION_URL = "https://telegra.ph/Instrukciya-dlya-bota-04-17"

captcha_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Я человек", callback_data="not_robot")
)


admin_markup = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Ответить пользователю", callback_data="answer")
).add(
    InlineKeyboardButton(text="Создать рассылку", callback_data="spam")
)


donation_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="На кофе", url=DONATION_URL)
)


instruciton_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Подробная инструкция", url=INSTRUCTION_URL)
)

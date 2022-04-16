from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


captcha_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="Я человек", callback_data="not_robot")
)


admin_markup = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton(text="Ответить пользователю", callback_data="answer")
).add(
    InlineKeyboardButton(text="Сбор статистики", callback_data="get_stat")
).add(
    InlineKeyboardButton(text="Создать рассылку", callback_data="spam")
)


donation_markup = InlineKeyboardMarkup().add(
    InlineKeyboardButton(text="На кофе", url="https://github.com/")
)

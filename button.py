from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


DONATION_URL = "https://yoomoney.ru/quickpay/shop-widget?writer=seller&targets=%D0%9D%D0%B0%20%D0%BA%D0%BE%D1%84%D0%B5%20%D1%80%D0%B0%D0%B7%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%87%D0%B8%D0%BA%D1%83&default-sum=100&button-text=14&payment-type-choice=on&successURL=&quickpay=shop&account=410013484924202&"

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

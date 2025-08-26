from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📚 Категории"), KeyboardButton(text="🔥 Популярное")],
            [KeyboardButton(text="🔎 Поиск"), KeyboardButton(text="✉️ Задать вопрос")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Напишите вопрос или выберите пункт"
    )

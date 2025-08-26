from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

POPULAR_BTN = "🔥 Популярное"


def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📚 Категории"), KeyboardButton(text=POPULAR_BTN)],
        [KeyboardButton(text="🔎 Поиск"), KeyboardButton(text="✉️ Задать вопрос")],
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Напишите вопрос или выберите пункт",
        selective=True,
    )

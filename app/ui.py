from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

def search_results_kb(items: list[tuple[str,int,str,int]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for cat_id, idx, q, _score in items:
        kb.button(text=q, callback_data=f"faq:{cat_id}:{int(idx)}")
    kb.button(text="◀️ Категории", callback_data="menu:root")
    kb.adjust(1)
    return kb.as_markup()

def answer_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="👍 Полезно", callback_data="fb:up")
    kb.button(text="👎 Не помогло", callback_data="fb:down")
    kb.button(text="⬅️ В меню", callback_data="menu:root")
    kb.adjust(2,1)
    return kb.as_markup()

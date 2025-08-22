from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="📚 Категории", callback_data="menu:cats")
    kb.button(text="🔥 Популярное", callback_data="menu:popular")
    kb.button(text="🔎 Поиск", callback_data="menu:search")
    kb.button(text="✉️ Задать вопрос", callback_data="menu:ask")
    kb.adjust(2,2)
    return kb.as_markup()

def back_menu_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ В меню", callback_data="menu:root")
    return kb.as_markup()

def categories_kb(categories):
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=c.title or c.id, callback_data=f"cat:{c.id}:0")
    kb.button(text="⬅️ В меню", callback_data="menu:root")
    kb.adjust(2)
    return kb.as_markup()

def category_items_kb(cat_id: str, titles: list[str], page: int, page_size: int = 8):
    kb = InlineKeyboardBuilder()
    start = page*page_size
    for i, title in enumerate(titles[start:start+page_size], start=start):
        kb.button(text=title[:64], callback_data=f"q:{cat_id}:{i}")
    # пагинация
    nav = []
    if page > 0:
        nav.append(("◀️ Назад", f"cat:{cat_id}:{page-1}"))
    if start + page_size < len(titles):
        nav.append(("Вперёд ▶️", f"cat:{cat_id}:{page+1}"))
    for t, d in nav:
        kb.button(text=t, callback_data=d)
    kb.button(text="⬅️ Категории", callback_data="menu:cats")
    kb.adjust(1)
    return kb.as_markup()


def search_results_kb(results):
    kb = InlineKeyboardBuilder()
    for cat_id, idx, q, score in results:
        kb.button(text=q[:64], callback_data=f"q:{cat_id}:{idx}")
    kb.button(text="✉️ Задать вопрос", callback_data="menu:ask")
    kb.button(text="⬅️ В меню", callback_data="menu:root")
    kb.adjust(1)
    return kb.as_markup()

def answer_kb(cat_id: str, idx: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="👍 Полезно", callback_data=f"hv:yes:{cat_id}:{idx}")
    kb.button(text="👎 Не помогло", callback_data=f"hv:no:{cat_id}:{idx}")
    kb.button(text="⬅️ В меню", callback_data="menu:root")
    kb.adjust(2,1)
    return kb.as_markup()


def admin_reply_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Ответить", callback_data=f"reply:{user_id}")
    return kb.as_markup()
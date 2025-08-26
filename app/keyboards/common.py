from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔥 Популярное",  callback_data="menu:popular")],
        [InlineKeyboardButton(text="🔎 Поиск",       callback_data="menu:search")],
        [InlineKeyboardButton(text="📚 Категории",   callback_data="menu:cats")],
        [InlineKeyboardButton(text="✉️ Задать вопрос", callback_data="menu:ask")],
    ])

def back_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="menu:root")]
    ])

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
    return kb


def admin_reply_kb(user_id: int):
    kb = InlineKeyboardBuilder()
    kb.button(text="↩️ Ответить", callback_data=f"reply:{user_id}")
    return kb.as_markup()


def answer_links_kb(buttons: list[dict], base=None):
    kb = base or InlineKeyboardBuilder()
    for b in buttons or []:
        t, u = b.get("text","").strip(), b.get("url","").strip()
        if t and u:
            kb.button(text=t[:64], url=u)
    return kb


def related_kb(related: list[tuple[str,int,str]], base=None):
    kb = base or InlineKeyboardBuilder()
    for cat_id, idx, q in related[:3]:
        kb.button(text=f"🔁 {q[:56]}", callback_data=f"q:{cat_id}:{idx}")
    return kb
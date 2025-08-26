from aiogram import Router, F
from aiogram.types import Message

from ..services import registry
from ..keyboards.common import categories_kb, search_results_kb
from ..keyboards.reply import main_menu_kb

router = Router(name="fallback_routes")

def _not_ready():
    return (registry.store is None) or (registry.searcher is None)

@router.message(F.text == "📚 Категории")
async def show_categories(m: Message):
    if _not_ready():
        await m.answer("Сервис инициализируется, попробуйте ещё раз.", reply_markup=main_menu_kb())
        return
    cats = registry.store.list_categories()
    await m.answer("Категории:", reply_markup=categories_kb(cats))

@router.message(F.text == "🔥 Популярное")
async def show_popular(m: Message):
    if _not_ready():
        await m.answer("Сервис инициализируется, попробуйте ещё раз.", reply_markup=main_menu_kb())
        return
    results = []
    for t in registry.store.popular_titles():
        key = registry.store.lookup_by_question(t)
        if not key:
            continue
        cat_id, idx = key
        results.append((cat_id, int(idx), t, 100))
    if not results:
        await m.answer("Пока нет популярных вопросов.")
        return
    await m.answer("Популярное:", reply_markup=search_results_kb(results))

@router.message(F.text == "🔎 Поиск")
async def prompt_search(m: Message):
    await m.answer("Введите слово или фразу для поиска.", reply_markup=main_menu_kb())

@router.message(F.text == "✉️ Задать вопрос")
async def ask_entry(m: Message):
    # Текстовая кнопка не может вызвать callback, поэтому просто направляем в меню
    await m.answer("Нажмите «Меню → Задать вопрос» и опишите проблему одним сообщением.", reply_markup=main_menu_kb())

@router.message(F.text & ~F.text.startswith("/"))
async def free_text_search(m: Message):
    if _not_ready():
        await m.answer("Сервис инициализируется, попробуйте ещё раз.", reply_markup=main_menu_kb())
        return
    q = (m.text or "").strip()
    if len(q) < 2:
        await m.answer("Короткий запрос. Напишите длиннее или выберите пункт меню.", reply_markup=main_menu_kb())
        return
    hits = registry.searcher.search(q, limit=8, cutoff=55)
    if not hits:
        await m.answer("Ничего не нашёл. Попробуйте иначе.", reply_markup=main_menu_kb())
        return
    await m.answer("Нашёл варианты:", reply_markup=search_results_kb(hits))


from aiogram import Router, F
from aiogram.types import Message
from app.services import registry
from app.keyboards.common import categories_kb, category_items_kb, search_results_kb
from app.keyboards.reply import main_menu_kb
from app.keyboards.common import search_results_kb


router = Router(name="fallback_routes")

@router.message(F.text == "📚 Категории")
async def show_categories(m: Message):
    cats = registry.store.categories
    await m.answer("Категории:", reply_markup=categories_kb(cats))

@router.message(F.text.lower().contains("популяр"))
async def show_popular(m: Message):
    titles = registry.store.popular_titles()  # ['Как оплатить...', ...]
    results = []
    for t in titles:
        key = registry.store.lookup_by_question(t)  # -> ('pay', 0) и т.п.
        if key:
            cat_id, idx = key
            results.append((cat_id, idx, t, 100))   # (cat_id, idx, q, score)

    if not results:
        await m.answer("Пока нет популярных вопросов.")
        return

    await m.answer("Популярное:", reply_markup=search_results_kb(results))

@router.message(F.text == "🔎 Поиск")
async def prompt_search(m: Message):
    await m.answer("Введите слово или фразу для поиска.", reply_markup=main_menu_kb())

@router.message(F.text == "✉️ Задать вопрос")
async def ask_entry(m: Message):
    # дерни существующий коллбек или просто напиши как старт сценария
    await m.answer("Опишите вопрос одним сообщением. Я перешлю админу.", reply_markup=main_menu_kb())

@router.message(F.text & ~F.text.startswith("/"))
async def free_text_search(m: Message):
    q = m.text.strip()
    if len(q) < 2:
        await m.answer("Короткий запрос. Напишите длиннее или выберите пункт меню.", reply_markup=main_menu_kb())
        return
    hits = registry.searcher.search(q, limit=8, cutoff=55)
    if not hits:
        await m.answer("Ничего не нашёл. Попробуйте иначе.", reply_markup=main_menu_kb())
        return
    await m.answer("Нашёл варианты:", reply_markup=search_results_kb(hits))

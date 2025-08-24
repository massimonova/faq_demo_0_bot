from ..config import settings
from ..services import analytics
from ..keyboards.common import (
    categories_kb, category_items_kb, search_results_kb, back_menu_kb, answer_kb)

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, InputMediaDocument
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from ..keyboards.common import (
    categories_kb, category_items_kb, search_results_kb, back_menu_kb,
    answer_kb, admin_reply_kb, answer_links_kb, related_kb
)
from ..services import registry, analytics


router = Router()

class SearchState(StatesGroup):
    waiting_query = State()

class AskState(StatesGroup):
    waiting_text = State()

# Категории
@router.callback_query(F.data == "menu:cats")
async def show_categories(c: CallbackQuery):
    cats = registry.store.list_categories()
    await c.message.edit_text("Выберите категорию:", reply_markup=categories_kb(cats))
    await c.answer()

@router.callback_query(F.data.startswith("cat:"))
async def show_category_items(c: CallbackQuery):
    _, cat_id, page = c.data.split(":")
    page = int(page)
    cat = registry.store.get_category(cat_id)
    titles = [it.q for it in cat.items]
    await c.message.edit_text(
        f"Категория: <b>{cat.title or cat.id}</b>",
        reply_markup=category_items_kb(cat_id, titles, page)
    )
    await c.answer()

# Показ конкретного ответа
@router.callback_query(F.data.startswith("q:"))
async def show_answer(c: CallbackQuery):
    _, cat_id, idx = c.data.split(":")
    idx = int(idx)
    item = registry.store.get_item(cat_id, idx)
    await analytics.inc_view(cat_id, idx)

    text = f"<b>Q:</b> {item.q}\n\n{item.a}"

    kb = answer_kb(cat_id, idx)                 # базовые кнопки
    kb = answer_links_kb(item.buttons, base=kb) # ссылки из YAML
    try:
        rel = []
        for r_cat, r_idx, r_q, _ in registry.searcher.search(item.q, limit=5, cutoff=50):
            if not (r_cat == cat_id and r_idx == idx):
                rel.append((r_cat, r_idx, r_q))
        kb = related_kb(rel, base=kb)           # похожие вопросы
    except Exception:
        pass

    markup = kb.as_markup()
    if item.media:
        m = item.media.lower()
        await c.message.delete()
        if m.endswith((".png",".jpg",".jpeg",".webp")):
            await c.message.answer_photo(item.media, caption=text, reply_markup=markup)
        else:
            await c.message.answer_document(item.media, caption=text, reply_markup=markup)
    else:
        await c.message.edit_text(text, reply_markup=markup)
    await c.answer()


# Популярное
@router.callback_query(F.data == "menu:popular")
async def show_popular(c: CallbackQuery):
    items = []
    for q in registry.store.popular():
        key = registry.store.lookup_by_question(q)
        if key:
            cat_id, idx = key
            items.append((cat_id, idx, q, 100))
    if not items:
        await c.message.edit_text("Популярные вопросы не настроены.", reply_markup=back_menu_kb())
    else:
        await c.message.edit_text("🔥 Популярное:", reply_markup=search_results_kb(items))
    await c.answer()

# Поиск
@router.callback_query(F.data == "menu:search")
async def ask_query(c: CallbackQuery, state: FSMContext):
    await state.set_state(SearchState.waiting_query)
    await c.message.edit_text("Напишите запрос для поиска по FAQ:", reply_markup=back_menu_kb())
    await c.answer()

@router.message(SearchState.waiting_query)
async def do_search(m: Message, state: FSMContext):
    q = (m.text or "").strip()
    results = registry.searcher.search(q, limit=6, cutoff=60)
    await analytics.log_search(m.from_user.id, q, len(results))  # ← лог

    if results:
        await m.answer("Результаты:", reply_markup=search_results_kb(results))
    else:
        await m.answer("Ничего не найдено. Можно <b>задать вопрос</b> оператору:", reply_markup=search_results_kb([]))
    await state.clear()


# «Задать вопрос»
@router.callback_query(F.data == "menu:ask")
async def start_ask(c: CallbackQuery, state: FSMContext):
    await state.set_state(AskState.waiting_text)
    await c.message.edit_text("Опишите вопрос одним сообщением. Я перешлю админу.", reply_markup=back_menu_kb())
    await c.answer()

@router.message(AskState.waiting_text)
async def collect_ask(m: Message, state: FSMContext):
    admin_id = settings.admin_id
    if not admin_id:
        await m.answer("ADMIN_ID не настроен.")
        await state.clear()
        return
    text = f"✉️ Вопрос от @{m.from_user.username or m.from_user.id} (id {m.from_user.id}):\n\n{m.text}"
    try:
        await m.bot.send_message(chat_id=admin_id, text=text, reply_markup=admin_reply_kb(m.from_user.id))
        await m.answer("Отправлено админу. Ожидайте ответ.")
    except Exception:
        await m.answer("Не удалось отправить админу. Проверьте ADMIN_ID.")
    await state.clear()


@router.callback_query(F.data.startswith("hv:yes:"))
async def helpful_yes(c: CallbackQuery):
    _, _, cat_id, idx = c.data.split(":")
    await analytics.mark_helpful(cat_id, int(idx), True)
    await c.answer("Спасибо")

@router.callback_query(F.data.startswith("hv:no:"))
async def helpful_no(c: CallbackQuery):
    _, _, cat_id, idx = c.data.split(":")
    await analytics.mark_helpful(cat_id, int(idx), False)
    await c.answer("Принято")



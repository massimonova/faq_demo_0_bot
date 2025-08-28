from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from ..config import settings
from ..keyboards.common import (
    categories_kb,
    category_items_kb,
    search_results_kb,
    back_menu_kb,
    answer_kb,
    admin_reply_kb,
)
from ..services import registry, analytics

router = Router()


class SearchState(StatesGroup):
    waiting_query = State()


class AskState(StatesGroup):
    waiting_text = State()


def _not_ready() -> bool:
    return (registry.store is None) or (registry.searcher is None)


# ===== Категории =====
@router.callback_query(F.data == "menu:cats")
async def show_categories(c: CallbackQuery):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    try:
        await c.answer()
    except Exception:
        pass
    cats = registry.store.list_categories()
    await c.message.edit_text(
        "Выберите категорию:",
        reply_markup=categories_kb(cats),
        disable_web_page_preview=True,
    )


@router.callback_query(F.data.startswith("cat:"))
async def show_category_items(c: CallbackQuery):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    try:
        await c.answer()
    except Exception:
        pass

    try:
        _, cat_id, page = c.data.split(":")
        page = int(page)
    except Exception:
        await c.message.answer("Некорректный пункт. Обновите список.", reply_markup=back_menu_kb())
        return

    cat = registry.store.get_category(cat_id)
    if not cat:
        await c.message.answer("Категория не найдена.", reply_markup=back_menu_kb())
        return

    titles = [it.q for it in cat.items]
    await c.message.edit_text(
        f"Категория: <b>{cat.title or cat.id}</b>",
        reply_markup=category_items_kb(cat_id, titles, page),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


# ===== Конкретный ответ =====
@router.callback_query(F.data.startswith("faq:"))
async def show_answer(cb: CallbackQuery):
    if _not_ready():
        await cb.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    try:
        await cb.answer()
    except Exception:
        pass

    try:
        _, cat_id, idx = cb.data.split(":")
        idx = int(idx)
    except Exception:
        await cb.message.answer("Некорректный пункт.", reply_markup=back_menu_kb())
        return

    item = registry.store.get_answer(cat_id, idx)
    if not item:
        await cb.message.answer("Ответ не найден. Обновите список.", reply_markup=back_menu_kb())
        return

    text = f"<b>Q:</b> {item.q}\n\n{item.a}"
    await cb.message.edit_text(
        text,
        reply_markup=answer_kb(),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


# ===== Популярное =====
@router.callback_query(F.data == "menu:popular")
async def popular_cb(c: CallbackQuery):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    try:
        await c.answer()
    except Exception:
        pass

    results = []
    for t in registry.store.popular_titles():
        key = registry.store.lookup_by_question(t)
        if key:
            cat_id, idx = key
            results.append((cat_id, int(idx), t, 100))

    if not results:
        await c.message.edit_text("Пока нет популярных вопросов.", reply_markup=back_menu_kb())
        return

    await c.message.edit_text("Популярное:", reply_markup=search_results_kb(results))


# ===== Поиск =====
@router.callback_query(F.data == "menu:search")
async def ask_query(c: CallbackQuery, state: FSMContext):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    await state.set_state(SearchState.waiting_query)
    try:
        await c.answer()
    except Exception:
        pass
    await c.message.edit_text("Напишите запрос для поиска по FAQ:", reply_markup=back_menu_kb())


@router.message(SearchState.waiting_query)
async def do_search(m: Message, state: FSMContext):
    if _not_ready():
        await m.answer("Сервис инициализируется, попробуйте ещё раз.", reply_markup=back_menu_kb())
        await state.clear()
        return

    q = (m.text or "").strip()
    results = registry.searcher.search(q, limit=6, cutoff=60)
    await analytics.log_search(m.from_user.id, q, len(results))

    if results:
        await m.answer("Результаты:", reply_markup=search_results_kb(results))
    else:
        await m.answer(
            "Ничего не найдено. Можно <b>задать вопрос</b> оператору:",
            reply_markup=search_results_kb([]),
            parse_mode="HTML",
        )
    await state.clear()


# ===== «Задать вопрос» =====
@router.callback_query(F.data == "menu:ask")
async def start_ask(c: CallbackQuery, state: FSMContext):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    await state.set_state(AskState.waiting_text)
    try:
        await c.answer()
    except Exception:
        pass
    await c.message.edit_text("Опишите вопрос одним сообщением. Я перешлю админу.", reply_markup=back_menu_kb())


@router.message(AskState.waiting_text)
async def collect_ask(m: Message, state: FSMContext):
    if _not_ready():
        await m.answer("Сервис инициализируется, попробуйте ещё раз.", reply_markup=back_menu_kb())
        await state.clear()
        return

    admin_id = int(settings.admin_id or 0)
    if not admin_id:
        await m.answer("ADMIN_ID не настроен.", reply_markup=back_menu_kb())
        await state.clear()
        return

    username = f"@{m.from_user.username}" if m.from_user.username else f"id:{m.from_user.id}"
    text = f"✉️ Вопрос от {username}:\n\n{m.text}"

    try:
        await m.bot.send_message(admin_id, text, reply_markup=admin_reply_kb(m.from_user.id))
        await m.answer("Отправлено админу. Ожидайте ответ.", reply_markup=back_menu_kb())
    except Exception:
        await m.answer(
            "Не удалось отправить админу. Проверьте ADMIN_ID (и что админ нажал /start у бота).",
            reply_markup=back_menu_kb(),
        )
    await state.clear()


# ===== Оценка полезности =====
@router.callback_query(F.data.startswith("hv:yes:"))
async def helpful_yes(c: CallbackQuery):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    try:
        await c.answer("Спасибо")
    except Exception:
        pass
    _, _, cat_id, idx = c.data.split(":")
    await analytics.mark_helpful(cat_id, int(idx), True)


@router.callback_query(F.data.startswith("hv:no:"))
async def helpful_no(c: CallbackQuery):
    if _not_ready():
        await c.answer("Сервис инициализируется, попробуйте ещё раз.", show_alert=True)
        return
    try:
        await c.answer("Принято")
    except Exception:
        pass
    _, _, cat_id, idx = c.data.split(":")
    await analytics.mark_helpful(cat_id, int(idx), False)

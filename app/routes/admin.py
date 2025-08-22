from aiogram import Router, F
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from ..config import settings
from ..services import analytics, registry

router = Router()
only_admin = F.from_user.id == settings.admin_id


class ReplyState(StatesGroup):
    waiting_text = State()


@router.message(only_admin, F.text == "/stats")
async def stats(m: Message):
    top = await analytics.top_questions(5)
    fails = await analytics.failed_queries(5)
    lines = ["Топ вопросов:"]
    for cat_id, idx, views, y, n in top:
        lines.append(f"{cat_id}:{idx} — views {views} 👍{y} 👎{n}")
    lines.append("\nНеудачные поиски:")
    for q, cnt in fails:
        lines.append(f"{q} — {cnt}")
    await m.answer("\n".join(lines) if len(lines) > 2 else "Пока пусто")

@router.message(only_admin, F.text == "/export_csv")
async def export_csv(m: Message):
    paths = await analytics.export_csv()
    for p in paths:
        await m.answer_document(FSInputFile(p))


@router.message(only_admin, F.text == "/diag_yaml")
async def diag_yaml(m: Message):
    s = registry.store
    if not s:
        await m.answer("Store не инициализирован.")
        return

    total_cats = len(s.categories)
    total_items = sum(len(c.items) for c in s.categories)
    lines = [
        f"Категорий: {total_cats}",
        f"Вопросов всего: {total_items}",
        "",
        "По категориям:"
    ]
    for c in s.categories:
        lines.append(f"- {c.id} ({c.title or '—'}): {len(c.items)}")

    # проверка popular
    missing = [q for q in s.popular() if not s.lookup_by_question(q)]
    lines.append("")
    if missing:
        lines.append("popular: есть НЕсовпадения:")
        lines += [f"- {q}" for q in missing]
    else:
        lines.append("popular: ок")

    await m.answer("\n".join(lines))


@router.callback_query(only_admin, F.data.startswith("reply:"))
async def start_reply(c: CallbackQuery, state: FSMContext):
    _, uid = c.data.split(":")
    await state.set_state(ReplyState.waiting_text)
    await state.update_data(target_id=int(uid))
    await c.message.reply(f"Напишите ответ для пользователя {uid} одним сообщением.")
    await c.answer()

@router.message(only_admin, ReplyState.waiting_text)
async def send_reply(m: Message, state: FSMContext):
    data = await state.get_data()
    uid = data.get("target_id")
    if not uid:
        await m.answer("Нет target_id.")
        await state.clear()
        return
    try:
        await m.bot.send_message(uid, f"Ответ оператора:\n\n{m.text}")
        await m.answer("Отправлено.")
    except Exception as e:
        await m.answer(f"Не смог отправить: {e}")
    await state.clear()
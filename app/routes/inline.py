from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.enums import ParseMode

from app.services import registry
from app.keyboards.common import answer_kb

router = Router(name="inline_routes")

@router.inline_query()
async def inline_search(q: InlineQuery):
    query = (q.query or "").strip()
    if not query:
        # Пустой запрос — ничего не показываем, только кнопку "Открыть бота"
        await q.answer(
            [],
            cache_time=1,
            is_personal=True,
            switch_pm_text="Открыть бота",
            switch_pm_parameter="start",
        )
        return

    results = registry.searcher.search(query, limit=10, cutoff=55) or []
    out = []
    for cat_id, idx, score in results:
        item = registry.store.get_item(cat_id, idx)
        title = item.q[:64]
        desc = (item.a or "")[:120]
        text = f"<b>Q:</b> {item.q}\n\n{item.a}"

        out.append(
            InlineQueryResultArticle(
                id=f"{cat_id}:{idx}",
                title=title,
                description=f"{cat_id} · {score:.0f}%",
                input_message_content=InputTextMessageContent(
                    message_text=text, parse_mode=ParseMode.HTML
                ),
                reply_markup=answer_kb(cat_id, idx),
            )
        )

    await q.answer(out, cache_time=0, is_personal=True)

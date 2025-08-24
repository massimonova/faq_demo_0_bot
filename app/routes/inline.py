from aiogram import Router
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from ..services import registry

router = Router()

@router.inline_query()
async def inline_search(q: InlineQuery):
    query = (q.query or "").strip()
    if len(query) < 2:
        # пустой ответ, чтобы Telegram понял, что бот жив
        await q.answer([], cache_time=1, is_personal=True)
        return

    results = registry.searcher.search(query, limit=10, cutoff=55)
    articles = []
    n = 0
    for cat_id, idx, question, score in results:
        n += 1
        item = registry.store.get_item(cat_id, idx)
        text = f"<b>Q:</b> {item.q}\n\n{item.a}"
        articles.append(
            InlineQueryResultArticle(
                id=str(n),
                title=question,
                description=f"{cat_id} · {score}%",
                input_message_content=InputTextMessageContent(
                    message_text=text,
                    parse_mode="HTML",
                ),
            )
        )

    if not articles:
        articles.append(
            InlineQueryResultArticle(
                id="0",
                title="Ничего не найдено",
                input_message_content=InputTextMessageContent(
                    message_text="Не найдено. Открой бота и задай вопрос оператору: /start"
                ),
            )
        )

    await q.answer(articles, cache_time=1, is_personal=True)

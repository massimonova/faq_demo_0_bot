from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from ..services import registry

router = Router()

@router.inline_query(F.query.len() >= 2)
async def inline_search(q: InlineQuery):
    query = q.query.strip()
    results = registry.searcher.search(query, limit=10, cutoff=55)

    articles = []
    for i, (cat_id, idx, question, score) in enumerate(results, start=1):
        item = registry.store.get_item(cat_id, idx)
        text = f"<b>Q:</b> {item.q}\n\n{item.a}"
        articles.append(
            InlineQueryResultArticle(
                id=f"{i}",
                title=question,
                description=f"Найдено в категории {cat_id} · {score}%",
                input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML")
            )
        )
    if not articles:
        articles = [InlineQueryResultArticle(
            id="0",
            title="Ничего не найдено",
            input_message_content=InputTextMessageContent(
                message_text="Ничего не найдено. Откройте бота и задайте вопрос оператору: /start"
            )
        )]
    await q.answer(articles, cache_time=5, is_personal=True)

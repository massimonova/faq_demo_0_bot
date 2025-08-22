import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.config import settings
from app.routes import start as start_routes
from app.routes import faq as faq_routes
from app.routes import admin as admin_routes
from app.services.faq_store import FaqStore
from app.services.faq_search import FaqSearcher
from app.services import registry
from app.services import analytics
from app.middlewares.logging import EventLogger, RateLimit

bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
dp.include_router(start_routes.router)
dp.include_router(faq_routes.router)
dp.include_router(admin_routes.router)

# middlewares
dp.message.middleware(EventLogger())
dp.callback_query.middleware(EventLogger())
dp.message.middleware(RateLimit())
dp.callback_query.middleware(RateLimit())

async def _reload_loop():
    while True:
        changed = registry.store.reload_if_changed()
        if changed:
            registry.searcher.rebuild()
            try:
                await bot.send_message(settings.admin_id, "♻️ FAQ обновлён из YAML")
            except Exception:
                pass
        await asyncio.sleep(5)

async def main():
    await analytics.init_db()  # ← создать таблицы
    registry.store = FaqStore("data/faq_ru.yaml")
    registry.searcher = FaqSearcher(registry.store)
    asyncio.create_task(_reload_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

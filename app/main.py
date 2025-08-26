import os, asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from app.config import settings
from app.services import registry, analytics
from app.services.faq_store import FaqStore
from app.services.faq_search import FaqSearcher

from app.routes import start as start_routes
from app.routes import faq as faq_routes
from app.routes import admin as admin_routes
from app.routes import inline as inline_routes
from app.routes import fallback as fallback_routes

BOT_TOKEN      = settings.bot_token
ADMIN_ID       = settings.admin_id
BASE_URL       = os.getenv("BASE_URL", "").rstrip("/")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "change-me")
WEBHOOK_PATH   = "/webhook"

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Роутеры (fallback строго последним)
dp.include_router(start_routes.router)
dp.include_router(faq_routes.router)
dp.include_router(admin_routes.router)
dp.include_router(inline_routes.router)
dp.include_router(fallback_routes.router)

# Мидлвари
from app.middlewares.logging import EventLogger, RateLimit
dp.message.middleware(EventLogger()); dp.callback_query.middleware(EventLogger())
dp.message.middleware(RateLimit());   dp.callback_query.middleware(RateLimit())

async def _reload_loop():
    while True:
        if registry.store.reload_if_changed():
            registry.searcher.rebuild()
            try:
                await bot.send_message(ADMIN_ID, "♻️ FAQ обновлён из YAML")
            except Exception:
                pass
        await asyncio.sleep(5)

async def on_startup(app: web.Application):
    # БД аналитики и FAQ
    await analytics.init_db()
    registry.store = FaqStore("data/faq_ru.yaml")
    registry.searcher = FaqSearcher(registry.store)

    # username бота — нужно для ссылок/логов
    me = await bot.get_me()
    registry.bot_username = me.username

    # авто-перезагрузка YAML
    asyncio.create_task(_reload_loop())

    # вебхук
    if BASE_URL:
        await bot.set_webhook(
            url=BASE_URL + WEBHOOK_PATH,
            secret_token=WEBHOOK_SECRET,
            drop_pending_updates=True,
        )

async def on_shutdown(app: web.Application):
    try:
        await bot.delete_webhook()
    except Exception:
        pass

def create_app() -> web.Application:
    app = web.Application()

    async def health(_): return web.Response(text="ok")
    app.add_routes([web.get("/", health), web.get("/healthz", health)])

    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET)\
        .register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot, on_startup=[on_startup], on_shutdown=[on_shutdown])
    return app

if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=int(os.getenv("PORT", "10000")))

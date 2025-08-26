from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb
from app.keyboards.common import answer_kb
from app.services import registry

router = Router(name="start_routes")

@router.message(CommandStart(deep_link=True))
async def start_with_param(m: Message):
    parts = m.text.split(maxsplit=1)
    if len(parts) > 1 and parts[1].startswith("qa:"):
        try:
            _, cat_id, idx = parts[1].split(":")
            idx = int(idx)
            item = registry.store.get_item(cat_id, idx)
            text = f"<b>Q:</b> {item.q}\n\n{item.a}"
            await m.answer(text, reply_markup=answer_kb(cat_id, idx))
            return
        except Exception:
            pass
    await m.answer("👋 Привет. Я FAQ-бот. Выберите действие или напишите вопрос.",
                   reply_markup=main_menu_kb())

@router.message(CommandStart())
async def start_cmd(m: Message):
    await m.answer("👋 Привет. Я FAQ-бот.\nВыберите действие:",
                   reply_markup=main_menu_kb())

@router.callback_query(F.data == "menu:root")
async def to_root(c: CallbackQuery):
    await c.message.edit_text("Выберите действие:", reply_markup=main_menu_kb())
    await c.answer()

@router.message(F.text == "/help")
async def help_cmd(m: Message):
    await m.answer("Я FAQ-бот: категории, поиск, популярное, связь с оператором. /start — меню.")

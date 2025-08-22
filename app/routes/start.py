from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from ..keyboards.common import main_menu_kb

router = Router()

@router.message(F.text == "/start")
async def start_cmd(m: Message):
    await m.answer(
        "👋 Привет. Я FAQ-бот.\nВыберите действие:",
        reply_markup=main_menu_kb()
    )

@router.callback_query(F.data == "menu:root")
async def to_root(c: CallbackQuery):
    await c.message.edit_text("Выберите действие:", reply_markup=main_menu_kb())
    await c.answer()


@router.message(F.text == "/help")
async def help_cmd(m: Message):
    await m.answer("Я FAQ-бот: категории, поиск, популярное, связь с оператором. /start — меню.")
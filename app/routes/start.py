from aiogram import Router, F
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from ..keyboards.reply import main_menu_kb

router = Router(name="start_routes")

@router.message(CommandStart())
async def cmd_start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Выберите действие:", reply_markup=main_menu_kb())

@router.callback_query(F.data == "menu:root")
async def back_to_menu(c: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await c.message.edit_text("Выберите действие:", reply_markup=main_menu_kb())
    except Exception:
        # если сообщение нельзя редактировать
        await c.message.answer("Выберите действие:", reply_markup=main_menu_kb())
    await c.answer()

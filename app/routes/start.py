from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from ..keyboards.common import main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Выберите действие:", reply_markup=main_menu_kb())


async def _send_menu(msg: Message):
    await msg.answer("Выберите действие:", reply_markup=main_menu_kb())



@router.callback_query(F.data == "menu:root")
async def back_to_menu(c: CallbackQuery, state: FSMContext):
    await state.clear()
    await c.message.edit_text("Выберите действие:", reply_markup=main_menu_kb())
    await c.answer()

@router.callback_query(F.data == "menu:root")
async def back_to_menu_cb(cb: CallbackQuery):
    await cb.message.edit_text("Выберите действие:", reply_markup=main_menu_kb())
    await cb.answer()

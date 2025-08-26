from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from app.keyboards.reply import main_menu_kb

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from app.keyboards.reply import main_menu_kb
from app.keyboards.common import answer_kb
from app.services import registry

router = Router(name="start_routes")


@router.callback_query(F.data == "menu:root")
async def to_root(c: CallbackQuery):
    await c.message.answer("Выберите действие:", reply_markup=main_menu_kb())
    await c.answer()
    
# ===== Задать вопрос (вернули рабочий поток) =====
class Ask(StatesGroup):
    waiting = State()

@router.message(F.text == "Задать вопрос")
@router.message(F.text == "✉️ Задать вопрос")
async def ask_start(m: Message, state: FSMContext):
    await state.set_state(Ask.waiting)
    await m.answer("Опишите вопрос одним сообщением. Я перешлю админу.")

@router.message(Ask.waiting)
async def ask_finish(m: Message, state: FSMContext):
    # при наличии admin_chat_id перешлём
    try:
        from app.config import settings
        if getattr(settings, "admin_chat_id", None):
            await m.copy_to(settings.admin_chat_id)
    except Exception:
        pass
    await state.clear()
    await m.answer("Спасибо! Вопрос передан.", reply_markup=main_menu_kb())

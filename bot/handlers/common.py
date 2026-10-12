from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from .. import keyboards as kb
from .. import texts as t
from ..db import Database
from ..filters import is_admin
from . import student

router = Router(name="common")


def _menu(user_id: int):
    return kb.admin_menu() if is_admin(user_id) else ReplyKeyboardRemove()


@router.message(CommandStart())
async def start(message: Message, command: CommandObject, state: FSMContext, db: Database) -> None:
    user = message.from_user
    await db.upsert_user(user.id, user.full_name, user.username)
    await state.clear()

    # Kartadagi havola: t.me/bot?start=<test kodi>
    if command.args:
        await student.enter_code(message, state, db, command.args)
        return

    text = t.WELCOME_ADMIN if is_admin(user.id) else t.WELCOME_STUDENT
    await message.answer(text, reply_markup=_menu(user.id))


@router.message(Command("cancel"))
@router.message(F.text == t.BTN_CANCEL)
async def cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t.CANCELLED, reply_markup=_menu(message.from_user.id))


@router.message(Command("ism"))
async def change_name(message: Message, state: FSMContext, db: Database) -> None:
    user = message.from_user
    await db.upsert_user(user.id, user.full_name, user.username)
    await state.clear()
    await state.set_state(student.Student.full_name)
    await message.answer(t.ASK_FULL_NAME)

from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from .. import texts as t
from ..db import Database
from ..filters import is_director
from ..utils import esc, menu_for
from . import student

router = Router(name="common")


async def show_welcome(message: Message, db: Database) -> None:
    uid = message.from_user.id
    if is_director(uid):
        text = t.WELCOME_DIRECTOR
    elif await db.is_teacher(uid):
        text = t.WELCOME_TEACHER
    else:
        text = t.WELCOME_STUDENT
    await message.answer(text, reply_markup=await menu_for(uid, db) or ReplyKeyboardRemove())


@router.message(CommandStart(deep_link=True))
async def start_with_payload(
    message: Message, command: CommandObject, state: FSMContext, db: Database, bot: Bot
) -> None:
    user = message.from_user
    await db.upsert_user(user.id, user.full_name, user.username)
    await state.clear()
    payload = command.args or ""

    # O'qituvchi taklifnomasi: /start teacher_<token>
    if payload.startswith("teacher_"):
        if is_director(user.id) or await db.is_teacher(user.id):
            await message.answer(t.INVITE_ALREADY_TEACHER, reply_markup=await menu_for(user.id, db))
            return
        director_id = await db.use_teacher_invite(payload.removeprefix("teacher_"), user.id)
        if director_id is None:
            await message.answer(t.INVITE_INVALID)
            return
        await message.answer(t.INVITE_OK, reply_markup=await menu_for(user.id, db))
        try:
            await bot.send_message(director_id, t.INVITE_USED_NOTIFY.format(name=esc(user.full_name)))
        except Exception:
            pass
        return

    # Xonaga kirish: /start room_<code>
    if payload.startswith("room_"):
        room = await db.get_room_by_code(payload.removeprefix("room_"))
        if room is None:
            await message.answer(t.ROOM_LINK_INVALID)
            return
        await student.join_room(message, state, db, room)
        return

    await show_welcome(message, db)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, db: Database) -> None:
    user = message.from_user
    await db.upsert_user(user.id, user.full_name, user.username)
    await state.clear()
    await show_welcome(message, db)


@router.message(Command("cancel"))
@router.message(F.text == t.BTN_CANCEL)
async def cancel(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    uid = message.from_user.id
    await message.answer(t.CANCELLED, reply_markup=await menu_for(uid, db) or ReplyKeyboardRemove())

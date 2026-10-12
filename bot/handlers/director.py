from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from .. import keyboards as kb
from .. import texts as t
from ..db import Database
from ..filters import IsDirector
from ..utils import esc, invite_link, safe_edit

router = Router(name="director")
router.message.filter(IsDirector())
router.callback_query.filter(IsDirector())


@router.message(F.text == t.BTN_ADD_TEACHER)
async def add_teacher(message: Message, state: FSMContext, db: Database, bot_username: str) -> None:
    await state.clear()
    token = await db.create_teacher_invite(message.from_user.id)
    await message.answer(
        t.INVITE_CREATED.format(link=invite_link(bot_username, token)),
        disable_web_page_preview=True,
    )


@router.message(F.text == t.BTN_TEACHERS)
async def list_teachers(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    teachers = await db.list_teachers()
    if not teachers:
        await message.answer(t.TEACHERS_EMPTY)
        return
    lines = [t.TEACHERS_TITLE.format(count=len(teachers))]
    for i, tch in enumerate(teachers, 1):
        lines.append(
            t.TEACHER_ROW.format(
                i=i,
                name=esc(kb.display_name(tch)),
                username=f" (@{esc(tch['username'])})" if tch.get("username") else "",
                id=tch["user_id"],
                rooms=tch["rooms_count"],
            )
        )
    await message.answer("\n".join(lines))


@router.message(F.text == t.BTN_REMOVE_TEACHER)
async def remove_teacher_menu(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    teachers = await db.list_teachers()
    if not teachers:
        await message.answer(t.TEACHERS_EMPTY)
        return
    await message.answer(t.REMOVE_TEACHER_CHOOSE, reply_markup=kb.teachers_remove_kb(teachers))


async def _teacher_name(db: Database, user_id: int) -> str:
    for tch in await db.list_teachers():
        if tch["user_id"] == user_id:
            return kb.display_name(tch)
    return str(user_id)


@router.callback_query(kb.TeacherCb.filter(F.action == "ask"))
async def remove_teacher_ask(call: CallbackQuery, callback_data: kb.TeacherCb, db: Database) -> None:
    name = await _teacher_name(db, callback_data.user_id)
    await safe_edit(
        call.message,
        t.REMOVE_TEACHER_CONFIRM.format(name=esc(name)),
        kb.teacher_remove_confirm_kb(callback_data.user_id),
    )
    await call.answer()


@router.callback_query(kb.TeacherCb.filter(F.action == "no"))
async def remove_teacher_no(call: CallbackQuery, db: Database) -> None:
    teachers = await db.list_teachers()
    if teachers:
        await safe_edit(call.message, t.REMOVE_TEACHER_CHOOSE, kb.teachers_remove_kb(teachers))
    else:
        await safe_edit(call.message, t.TEACHERS_EMPTY)
    await call.answer()


@router.callback_query(kb.TeacherCb.filter(F.action == "yes"))
async def remove_teacher_yes(
    call: CallbackQuery, callback_data: kb.TeacherCb, db: Database, bot: Bot
) -> None:
    name = await _teacher_name(db, callback_data.user_id)
    await db.remove_teacher(callback_data.user_id)
    await safe_edit(call.message, t.TEACHER_REMOVED.format(name=esc(name)))
    await call.answer()
    try:
        await bot.send_message(
            callback_data.user_id, t.TEACHER_REMOVED_NOTIFY, reply_markup=ReplyKeyboardRemove()
        )
    except Exception:
        pass

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import keyboards as kb
from .. import texts as t
from ..answers import count_correct, format_answers, parse_answers
from ..db import Database, Room
from ..utils import esc, send_materials

router = Router(name="student")


class Student(StatesGroup):
    full_name = State()
    answering = State()
    confirming = State()


async def join_room(message: Message, state: FSMContext, db: Database, room: Room) -> None:
    """O'quvchi xona havolasini bosganda chaqiriladi (common.start_with_payload dan)."""
    uid = message.from_user.id
    if await db.get_submission(room.id, uid):
        await message.answer(t.ALREADY_SUBMITTED.format(name=esc(room.name)))
        return

    await message.answer(t.JOINED_ROOM.format(name=esc(room.name)))
    await state.update_data(room_id=room.id)

    if not await db.get_full_name(uid):
        await state.set_state(Student.full_name)
        await message.answer(t.ASK_FULL_NAME)
        return

    await start_test(message, state, db, room)


async def start_test(message: Message, state: FSMContext, db: Database, room: Room) -> None:
    await message.answer(
        t.TEST_RULES.format(total=len(room.correct_answers), example=esc(room.answer_example))
    )
    await send_materials(message, await db.get_materials(room.id))
    await message.answer(t.TEST_END)
    await state.set_state(Student.answering)


async def _current_room(state: FSMContext, db: Database) -> Room | None:
    room_id = (await state.get_data()).get("room_id")
    return await db.get_room(room_id) if room_id else None


@router.message(Student.full_name, F.text)
async def full_name(message: Message, state: FSMContext, db: Database) -> None:
    name = " ".join(message.text.split())
    if not 3 <= len(name) <= 64 or name.startswith("/"):
        await message.answer(t.FULL_NAME_BAD)
        return
    await db.set_full_name(message.from_user.id, name)
    room = await _current_room(state, db)
    if room is None:
        await state.clear()
        await message.answer(t.ROOM_GONE)
        return
    await start_test(message, state, db, room)


@router.message(Student.full_name)
async def full_name_bad(message: Message) -> None:
    await message.answer(t.FULL_NAME_BAD)


@router.message(Student.answering, F.text)
@router.message(Student.confirming, F.text)
async def got_answers(message: Message, state: FSMContext, db: Database) -> None:
    room = await _current_room(state, db)
    if room is None:
        await state.clear()
        await message.answer(t.ROOM_GONE)
        return

    answers = parse_answers(message.text)
    if not answers:
        await message.answer(t.STUDENT_ANSWER_BAD.format(example=esc(room.answer_example)))
        return

    missing = [q for q in room.correct_answers if q not in answers]
    extra = [q for q in answers if q not in room.correct_answers]
    warn = ""
    if missing:
        warn += t.STUDENT_MISSING.format(numbers=", ".join(missing))
    if extra:
        warn += t.STUDENT_EXTRA.format(numbers=", ".join(extra))

    await state.update_data(answers=answers)
    await state.set_state(Student.confirming)
    await message.answer(
        t.STUDENT_CONFIRM.format(answers=format_answers(answers), missing=warn),
        reply_markup=kb.answer_confirm_kb(),
    )


@router.message(Student.answering)
@router.message(Student.confirming)
async def answers_not_text(message: Message) -> None:
    await message.answer(t.STUDENT_ANSWER_TEXT_ONLY)


@router.callback_query(kb.AnswerCb.filter(F.action == "no"), Student.confirming)
async def answers_no(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    room = await _current_room(state, db)
    await state.set_state(Student.answering)
    await call.message.edit_reply_markup(reply_markup=None)
    example = esc(room.answer_example) if room else ""
    await call.message.answer(t.STUDENT_RESEND.format(example=example))
    await call.answer()


@router.callback_query(kb.AnswerCb.filter(F.action == "yes"), Student.confirming)
async def answers_yes(call: CallbackQuery, state: FSMContext, db: Database, bot: Bot) -> None:
    data = await state.get_data()
    room = await _current_room(state, db)
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    if room is None:
        await call.message.answer(t.ROOM_GONE)
        return

    uid = call.from_user.id
    answers: dict[str, str] = data["answers"]
    correct = count_correct(room.correct_answers, answers)
    total = len(room.correct_answers)
    name = await db.get_full_name(uid) or call.from_user.full_name

    saved = await db.add_submission(room.id, uid, name, answers, correct, total)
    if not saved:
        await call.message.answer(t.ALREADY_SUBMITTED.format(name=esc(room.name)))
        return

    await call.message.answer(t.STUDENT_SUBMITTED)
    try:
        await bot.send_message(
            room.teacher_id,
            t.NEW_SUBMISSION_NOTIFY.format(room=esc(room.name), name=esc(name), correct=correct, total=total),
        )
    except Exception:
        pass


# Eski tugmalar bosilsa (holat allaqachon tugagan)
@router.callback_query(kb.AnswerCb.filter())
async def stale_answer_button(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=None)


# Hech qaysi handler tutmagan xabarlar
@router.message()
async def fallback(message: Message) -> None:
    await message.answer(t.UNKNOWN)

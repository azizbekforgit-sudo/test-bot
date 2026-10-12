from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import keyboards as kb
from .. import texts as t
from ..answers import count_correct, format_answers, parse_answers
from ..db import Database, Test
from ..timeutils import ACTIVE, FINISHED, UPCOMING, status_of
from ..utils import esc

router = Router(name="student")


class Student(StatesGroup):
    full_name = State()
    answering = State()
    confirming = State()


async def enter_code(message: Message, state: FSMContext, db: Database, code: str) -> None:
    """O'quvchi test kodini yuborganda (yoki karta havolasini bosganda) chaqiriladi."""
    test = await db.get_test_by_code(code)
    if test is None:
        await message.answer(t.CODE_NOT_FOUND.format(code=esc(code[:40])))
        return

    fmt = dict(code=esc(test.code), date=test.date, start=test.start_time, end=test.end_time)
    st = status_of(test)
    if st == UPCOMING:
        await message.answer(t.TEST_UPCOMING.format(**fmt))
        return
    if st == FINISHED:
        await message.answer(t.TEST_FINISHED.format(**fmt))
        return
    if await db.get_result(test.id, message.from_user.id):
        await message.answer(t.ALREADY_SUBMITTED.format(**fmt))
        return

    await state.clear()
    await state.update_data(test_id=test.id)
    await message.answer(t.JOINED_TEST.format(code=esc(test.code), title=esc(test.title)))

    if not await db.get_full_name(message.from_user.id):
        await state.set_state(Student.full_name)
        await message.answer(t.ASK_FULL_NAME)
        return
    await start_test(message, state, test)


async def start_test(message: Message, state: FSMContext, test: Test) -> None:
    if test.file_kind == "document":
        await message.answer_document(test.file_id)
    elif test.file_kind == "photo":
        await message.answer_photo(test.file_id)
    await message.answer(
        t.TEST_RULES.format(total=len(test.correct_answers), end=test.end_time, example=t.ANSWER_EXAMPLE)
    )
    await state.set_state(Student.answering)


async def _current_test(state: FSMContext, db: Database) -> Test | None:
    test_id = (await state.get_data()).get("test_id")
    return await db.get_test(test_id) if test_id else None


# =============== ism-familiya ===============

@router.message(Student.full_name, F.text)
async def full_name(message: Message, state: FSMContext, db: Database) -> None:
    name = " ".join(message.text.split())
    if not 3 <= len(name) <= 64 or name.startswith("/"):
        await message.answer(t.FULL_NAME_BAD)
        return
    await db.set_full_name(message.from_user.id, name)
    test = await _current_test(state, db)
    if test is None:  # /ism buyrug'i orqali o'zgartirildi
        await state.clear()
        await message.answer(t.FULL_NAME_SAVED.format(name=esc(name)))
        return
    if status_of(test) != ACTIVE:
        await state.clear()
        await message.answer(t.TIME_IS_UP.format(end=test.end_time))
        return
    await start_test(message, state, test)


@router.message(Student.full_name)
async def full_name_bad(message: Message) -> None:
    await message.answer(t.FULL_NAME_BAD)


# =============== javoblar ===============

@router.message(Student.answering, F.text)
@router.message(Student.confirming, F.text)
async def got_answers(message: Message, state: FSMContext, db: Database) -> None:
    test = await _current_test(state, db)
    if test is None:
        await state.clear()
        await message.answer(t.TEST_GONE)
        return
    if status_of(test) == FINISHED:
        await state.clear()
        await message.answer(t.TIME_IS_UP.format(end=test.end_time))
        return

    answers = parse_answers(message.text)
    if not answers:
        await message.answer(t.STUDENT_ANSWER_BAD.format(example=t.ANSWER_EXAMPLE))
        return

    missing = [q for q in test.correct_answers if q not in answers]
    extra = [q for q in answers if q not in test.correct_answers]
    warn = ""
    if missing:
        warn += t.STUDENT_MISSING.format(numbers=", ".join(missing))
    if extra:
        warn += t.STUDENT_EXTRA.format(numbers=", ".join(extra))

    await state.update_data(answers=answers)
    await state.set_state(Student.confirming)
    await message.answer(
        t.STUDENT_CONFIRM.format(answers=format_answers(answers), warn=warn),
        reply_markup=kb.answer_confirm_kb(),
    )


@router.message(Student.answering)
@router.message(Student.confirming)
async def answers_not_text(message: Message) -> None:
    await message.answer(t.STUDENT_ANSWER_TEXT_ONLY)


@router.callback_query(kb.AnswerCb.filter(F.action == "no"), Student.confirming)
async def answers_no(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(Student.answering)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t.STUDENT_RESEND.format(example=t.ANSWER_EXAMPLE))
    await call.answer()


@router.callback_query(kb.AnswerCb.filter(F.action == "yes"), Student.confirming)
async def answers_yes(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    test = await _current_test(state, db)
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    if test is None:
        await call.message.answer(t.TEST_GONE)
        return
    # Vaqt «Ha» bosilgan paytda ham tekshiriladi
    if status_of(test) == FINISHED:
        await call.message.answer(t.TIME_IS_UP.format(end=test.end_time))
        return

    uid = call.from_user.id
    answers: dict[str, str] = data["answers"]
    name = await db.get_full_name(uid) or call.from_user.full_name
    saved = await db.add_result(
        test.id, uid, name, answers, count_correct(test.correct_answers, answers), len(test.correct_answers)
    )
    if not saved:
        await call.message.answer(t.ALREADY_SUBMITTED.format(code=esc(test.code)))
        return
    await call.message.answer(t.STUDENT_SUBMITTED)


# Eski tugmalar bosilsa (holat allaqachon tugagan)
@router.callback_query(kb.AnswerCb.filter())
async def stale_answer_button(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.edit_reply_markup(reply_markup=None)


# =============== test kodi ===============

@router.message(F.text, ~F.text.startswith("/"))
async def code_message(message: Message, state: FSMContext, db: Database) -> None:
    await enter_code(message, state, db, message.text.strip())


@router.message()
async def fallback(message: Message) -> None:
    await message.answer(t.WELCOME_STUDENT)

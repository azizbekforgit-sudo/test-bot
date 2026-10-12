import asyncio

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import keyboards as kb
from .. import texts as t
from ..answers import format_answers, grade, parse_answers
from ..db import Database, Room
from ..filters import IsTeacher
from ..utils import esc, menu_for, room_link, safe_edit, send_materials

router = Router(name="teacher")
router.message.filter(IsTeacher())
router.callback_query.filter(IsTeacher())


class CreateRoom(StatesGroup):
    name = State()
    test = State()
    example = State()
    correct = State()
    confirm = State()


# Test qismlari (matn/rasm/fayl) shu yerda vaqtincha yig'iladi.
# Albom (bir nechta rasm) bir vaqtda keladi, shuning uchun FSM o'rniga
# oddiy lug'atdan foydalanamiz — ro'yxatga qo'shish atomar bo'ladi.
_drafts: dict[int, list[dict]] = {}
_seen_albums: dict[int, set[str]] = {}


# =============== menyu tugmalari ===============
# (birinchi turadi, shunda boshqa holatlarda ham ishlaydi)

@router.message(F.text == t.BTN_MY_ROOMS)
async def my_rooms(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    rooms = await db.list_rooms(message.from_user.id)
    if not rooms:
        await message.answer(t.ROOMS_EMPTY.format(create=t.BTN_CREATE_ROOM))
        return
    await message.answer(t.ROOMS_TITLE, reply_markup=kb.rooms_kb(rooms))


# =============== xona yaratish ===============

@router.message(F.text == t.BTN_CREATE_ROOM)
async def create_room_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(CreateRoom.name)
    await message.answer(t.ASK_ROOM_NAME, reply_markup=kb.cancel_menu())


@router.message(CreateRoom.name, F.text)
async def room_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not 1 <= len(name) <= 64 or name.startswith("/"):
        await message.answer(t.ROOM_NAME_BAD)
        return
    uid = message.from_user.id
    _drafts[uid] = []
    _seen_albums[uid] = set()
    await state.update_data(name=name)
    await state.set_state(CreateRoom.test)
    await message.answer(t.ASK_TEST.format(done=t.BTN_DONE), reply_markup=kb.test_done_kb())


@router.message(CreateRoom.name)
async def room_name_bad(message: Message) -> None:
    await message.answer(t.ROOM_NAME_BAD)


@router.message(CreateRoom.test)
async def test_part(message: Message) -> None:
    uid = message.from_user.id
    parts = _drafts.setdefault(uid, [])
    if message.photo:
        parts.append({"kind": "photo", "file_id": message.photo[-1].file_id, "text": message.html_text})
    elif message.document:
        parts.append({"kind": "document", "file_id": message.document.file_id, "text": message.html_text})
    elif message.text:
        parts.append({"kind": "text", "text": message.html_text})
    else:
        await message.answer(t.TEST_PART_BAD)
        return

    # Albomdagi har bir rasmga alohida javob yozmaslik uchun
    if message.media_group_id:
        seen = _seen_albums.setdefault(uid, set())
        if message.media_group_id in seen:
            return
        seen.add(message.media_group_id)
        await asyncio.sleep(1)  # albomning qolgan rasmlari ham kelib ulgursin

    await message.answer(
        t.TEST_PART_SAVED.format(count=len(parts), done=t.BTN_DONE),
        reply_markup=kb.test_done_kb(),
    )


@router.callback_query(kb.TestCb.filter(F.action == "done"), CreateRoom.test)
async def test_done(call: CallbackQuery, state: FSMContext) -> None:
    uid = call.from_user.id
    parts = _drafts.get(uid) or []
    if not parts:
        await call.answer(t.TEST_EMPTY, show_alert=True)
        return
    await state.update_data(materials=list(parts))
    _drafts.pop(uid, None)
    _seen_albums.pop(uid, None)
    await state.set_state(CreateRoom.example)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t.ASK_EXAMPLE)
    await call.answer()


@router.message(CreateRoom.example, F.text)
async def answer_example(message: Message, state: FSMContext) -> None:
    if not parse_answers(message.text):
        await message.answer(t.EXAMPLE_BAD)
        return
    await state.update_data(example=message.text.strip())
    await state.set_state(CreateRoom.correct)
    await message.answer(t.ASK_CORRECT)


@router.message(CreateRoom.example)
async def answer_example_bad(message: Message) -> None:
    await message.answer(t.EXAMPLE_BAD)


@router.message(CreateRoom.correct, F.text)
@router.message(CreateRoom.confirm, F.text)
async def correct_answers(message: Message, state: FSMContext) -> None:
    answers = parse_answers(message.text)
    if not answers:
        await message.answer(t.CORRECT_BAD)
        return
    await state.update_data(correct=answers)
    await state.set_state(CreateRoom.confirm)
    rows = "\n".join(f"{q}. {a}" for q, a in answers.items())
    await message.answer(
        t.CORRECT_CONFIRM.format(total=len(answers), answers=rows),
        reply_markup=kb.correct_confirm_kb(),
    )


@router.message(CreateRoom.correct)
@router.message(CreateRoom.confirm)
async def correct_answers_not_text(message: Message) -> None:
    await message.answer(t.ASK_CORRECT)


@router.callback_query(kb.TestCb.filter(F.action == "correct_no"), CreateRoom.confirm)
async def correct_no(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(CreateRoom.correct)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t.ASK_CORRECT)
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "correct_yes"), CreateRoom.confirm)
async def correct_yes(call: CallbackQuery, state: FSMContext, db: Database, bot_username: str) -> None:
    data = await state.get_data()
    await state.clear()
    room = await db.create_room(
        teacher_id=call.from_user.id,
        name=data["name"],
        answer_example=data["example"],
        correct_answers=data["correct"],
        materials=data["materials"],
    )
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        t.ROOM_CREATED.format(
            name=esc(room.name),
            total=len(room.correct_answers),
            link=room_link(bot_username, room.code),
        ),
        reply_markup=await menu_for(call.from_user.id, db),
        disable_web_page_preview=True,
    )
    await call.answer()


# =============== mavjud xonalar ===============

@router.callback_query(kb.RoomCb.filter(F.action == "list"))
async def rooms_list_cb(call: CallbackQuery, callback_data: kb.RoomCb, db: Database) -> None:
    rooms = await db.list_rooms(call.from_user.id)
    if not rooms:
        await safe_edit(call.message, t.ROOMS_EMPTY.format(create=t.BTN_CREATE_ROOM))
    else:
        await safe_edit(call.message, t.ROOMS_TITLE, kb.rooms_kb(rooms, callback_data.page))
    await call.answer()


async def _own_room(call: CallbackQuery, db: Database, room_id: int) -> Room | None:
    room = await db.get_room(room_id)
    if room is None or room.teacher_id != call.from_user.id:
        await call.answer(t.ROOM_NOT_FOUND, show_alert=True)
        return None
    return room


async def _show_room(call: CallbackQuery, db: Database, room: Room, page: int, bot_username: str) -> None:
    subs = await db.list_submissions(room.id)
    body = t.ROOM_SUBS_HINT if subs else t.ROOM_NO_SUBS
    text = t.ROOM_VIEW.format(
        name=esc(room.name),
        total=len(room.correct_answers),
        count=len(subs),
        link=room_link(bot_username, room.code),
        body=body,
    )
    await safe_edit(call.message, text, kb.room_kb(room.id, subs, page))


@router.callback_query(kb.RoomCb.filter(F.action == "open"))
async def room_open(call: CallbackQuery, callback_data: kb.RoomCb, db: Database, bot_username: str) -> None:
    room = await _own_room(call, db, callback_data.room_id)
    if room is None:
        return
    await _show_room(call, db, room, callback_data.page, bot_username)
    await call.answer()


@router.callback_query(kb.SubCb.filter())
async def submission_detail(call: CallbackQuery, callback_data: kb.SubCb, db: Database) -> None:
    sub = await db.get_submission_by_id(callback_data.sub_id)
    room = await _own_room(call, db, sub.room_id) if sub else None
    if room is None:
        if sub is None:
            await call.answer(t.ROOM_NOT_FOUND, show_alert=True)
        return
    rows = []
    for r in grade(room.correct_answers, sub.answers):
        given = r.given or t.NO_ANSWER
        if r.is_correct:
            rows.append(t.SUB_ROW_OK.format(q=r.number, given=given))
        else:
            rows.append(t.SUB_ROW_BAD.format(q=r.number, given=given, correct=r.correct))
    text = t.SUB_DETAIL.format(
        name=esc(sub.student_name),
        room=esc(room.name),
        correct=sub.correct_count,
        total=sub.total,
        time=sub.submitted_at.replace("T", " "),
        rows="\n".join(rows),
    )
    await safe_edit(call.message, text, kb.sub_back_kb(room.id, callback_data.page))
    await call.answer()


@router.callback_query(kb.RoomCb.filter(F.action == "link"))
async def room_link_cb(call: CallbackQuery, callback_data: kb.RoomCb, db: Database, bot_username: str) -> None:
    room = await _own_room(call, db, callback_data.room_id)
    if room is None:
        return
    await call.message.answer(
        t.ROOM_LINK.format(name=esc(room.name), link=room_link(bot_username, room.code)),
        disable_web_page_preview=True,
    )
    await call.answer()


@router.callback_query(kb.RoomCb.filter(F.action == "test"))
async def room_test_cb(call: CallbackQuery, callback_data: kb.RoomCb, db: Database) -> None:
    room = await _own_room(call, db, callback_data.room_id)
    if room is None:
        return
    await call.answer()
    await send_materials(call.message, await db.get_materials(room.id))
    await call.message.answer(
        t.TEST_ANSWERS.format(
            total=len(room.correct_answers),
            answers=format_answers(room.correct_answers),
        )
    )


@router.callback_query(kb.RoomCb.filter(F.action == "send"))
async def send_results(
    call: CallbackQuery, callback_data: kb.RoomCb, db: Database, bot: Bot, bot_username: str
) -> None:
    room = await _own_room(call, db, callback_data.room_id)
    if room is None:
        return
    pending = [s for s in await db.list_submissions(room.id) if not s.result_sent]
    if not pending:
        await call.answer(t.RESULTS_NOTHING, show_alert=True)
        return
    await call.answer()

    ok = failed = 0
    for sub in pending:
        wrong_rows = [
            t.STUDENT_RESULT_WRONG_ROW.format(q=r.number, given=r.given or t.NO_ANSWER)
            for r in grade(room.correct_answers, sub.answers)
            if not r.is_correct
        ]
        wrong = (
            t.STUDENT_RESULT_WRONG.format(rows="\n".join(wrong_rows))
            if wrong_rows
            else t.STUDENT_RESULT_PERFECT
        )
        try:
            await bot.send_message(
                sub.student_id,
                t.STUDENT_RESULT.format(
                    room=esc(room.name), correct=sub.correct_count, total=sub.total, wrong=wrong
                ),
            )
            await db.mark_result_sent(sub.id)
            ok += 1
        except TelegramAPIError:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram cheklovlariga tushmaslik uchun

    await call.message.answer(
        t.RESULTS_SENT.format(ok=ok, failed=t.RESULTS_FAILED.format(n=failed) if failed else "")
    )
    await _show_room(call, db, room, 0, bot_username)


@router.callback_query(kb.RoomCb.filter(F.action == "del"))
async def room_delete_ask(call: CallbackQuery, callback_data: kb.RoomCb, db: Database) -> None:
    room = await _own_room(call, db, callback_data.room_id)
    if room is None:
        return
    await safe_edit(call.message, t.ROOM_DELETE_CONFIRM.format(name=esc(room.name)), kb.room_delete_kb(room.id))
    await call.answer()


@router.callback_query(kb.RoomCb.filter(F.action == "del_yes"))
async def room_delete_yes(call: CallbackQuery, callback_data: kb.RoomCb, db: Database) -> None:
    room = await _own_room(call, db, callback_data.room_id)
    if room is None:
        return
    await db.delete_room(room.id)
    await call.answer(t.ROOM_DELETED)
    rooms = await db.list_rooms(call.from_user.id)
    if rooms:
        await safe_edit(call.message, t.ROOMS_TITLE, kb.rooms_kb(rooms))
    else:
        await safe_edit(call.message, t.ROOMS_EMPTY.format(create=t.BTN_CREATE_ROOM))

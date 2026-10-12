import asyncio
from types import SimpleNamespace

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .. import form
from .. import keyboards as kb
from .. import texts as t
from ..answers import format_answers, grade
from ..card import build_card, channel_username, send_card
from ..db import Database, Test
from ..filters import IsAdmin
from ..timeutils import FINISHED, status_of
from ..utils import esc, percent, safe_edit

router = Router(name="admin")
router.message.filter(IsAdmin())
router.callback_query.filter(IsAdmin())


class Form(StatesGroup):
    value = State()     # maydon qiymatini kutyapmiz
    preview = State()   # qoralama tayyor, «Saqlash»ni kutyapmiz
    channel = State()   # kanal havolasini kutyapmiz


# Nusxa olinganda qayta so'raladigan maydonlar tozalanadi
CLONE_RESET = {"date": None, "start_time": None, "end_time": None, "code": None}
TIME_FIELDS = {"date", "start_time", "end_time"}


async def _channel(db: Database) -> str | None:
    return await db.get_setting("channel") or None


# =============== menyu tugmalari ===============

@router.message(F.text == t.BTN_NEW_TEST)
async def new_test(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    if await db.get_setting("channel") is None:
        # Kanal faqat bir marta so'raladi, keyin bot uni eslab qoladi
        await state.set_state(Form.channel)
        await state.update_data(then_new=True)
        await message.answer(t.ASK_CHANNEL, reply_markup=kb.cancel_menu())
        return
    await message.answer(t.NEW_TEST_CHOOSE, reply_markup=kb.new_test_kb())


@router.message(F.text == t.BTN_TESTS)
async def tests_list(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    tests = await db.list_tests()
    if not tests:
        await message.answer(t.NO_TESTS.format(new=t.BTN_NEW_TEST))
        return
    statuses = {test.id: status_of(test) for test, _ in tests}
    await message.answer(t.TESTS_TITLE, reply_markup=kb.tests_kb(tests, statuses))


@router.message(F.text == t.BTN_SETTINGS)
async def settings(message: Message, state: FSMContext, db: Database, bot_username: str) -> None:
    await state.clear()
    await message.answer(
        t.SETTINGS_VIEW.format(channel=esc(await _channel(db) or t.NO_CHANNEL), bot=bot_username),
        reply_markup=kb.settings_kb(),
    )


# =============== sozlamalar: kanal ===============

@router.callback_query(kb.SetCb.filter(F.action == "channel"))
async def change_channel(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(Form.channel)
    await call.message.answer(t.ASK_CHANNEL, reply_markup=kb.cancel_menu())
    await call.answer()


@router.message(Form.channel, F.text)
async def got_channel(message: Message, state: FSMContext, db: Database) -> None:
    text = message.text.strip()
    if text == "-":
        value = ""
    else:
        username = channel_username(text)
        if not username:
            await message.answer(t.CHANNEL_BAD)
            return
        value = f"@{username}"
    then_new = (await state.get_data()).get("then_new")
    await state.clear()
    await db.set_setting("channel", value)
    await message.answer(t.CHANNEL_SAVED.format(channel=value or t.NO_CHANNEL), reply_markup=kb.admin_menu())
    if then_new:
        await message.answer(t.NEW_TEST_CHOOSE, reply_markup=kb.new_test_kb())


@router.message(Form.channel)
async def got_channel_bad(message: Message) -> None:
    await message.answer(t.CHANNEL_BAD)


# =============== yangi test: noldan yoki nusxa ===============

@router.callback_query(kb.NewCb.filter(F.action == "scratch"))
async def new_from_scratch(call: CallbackQuery, state: FSMContext, db: Database, bot_username: str) -> None:
    await state.set_data({"draft": {}, "queue": list(form.NEW_TEST_ORDER), "test_id": 0})
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t.BLANK_CARD_INTRO, reply_markup=kb.cancel_menu())
    await call.message.answer(
        build_card({}, bot_username, await _channel(db), blank=True), disable_web_page_preview=True
    )
    await call.answer()
    await ask_next(call.message, state, db)


@router.callback_query(kb.NewCb.filter(F.action == "old"))
async def new_from_old(call: CallbackQuery, db: Database) -> None:
    tests = await db.list_tests()
    if not tests:
        await call.answer(t.NO_TESTS.format(new=t.BTN_NEW_TEST), show_alert=True)
        return
    statuses = {test.id: status_of(test) for test, _ in tests}
    await safe_edit(call.message, t.PICK_OLD_TEST, kb.tests_kb(tests, statuses, pick=True))
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "pick"))
async def pick_page(call: CallbackQuery, callback_data: kb.TestCb, db: Database) -> None:
    tests = await db.list_tests()
    statuses = {test.id: status_of(test) for test, _ in tests}
    await safe_edit(call.message, t.PICK_OLD_TEST, kb.tests_kb(tests, statuses, callback_data.page, pick=True))
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "clone"))
async def clone_test(call: CallbackQuery, callback_data: kb.TestCb, state: FSMContext, db: Database) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    draft = {**test.to_draft(), **CLONE_RESET}
    await state.set_data({"draft": draft, "queue": list(form.CLONE_ORDER), "test_id": 0})
    await call.message.answer(
        t.CLONE_INTRO.format(title=esc(test.title), edit=t.BTN_EDIT), reply_markup=kb.cancel_menu()
    )
    await call.answer()
    await ask_next(call.message, state, db)


# =============== maydonlarni so'rash ===============

async def ask_next(message: Message, state: FSMContext, db: Database) -> None:
    """Navbatdagi maydonni so'raydi. Navbat tugasa — kartani ko'rsatadi."""
    data = await state.get_data()
    queue = data.get("queue") or []
    if not queue:
        await show_preview(message, state, db, message.bot)
        return
    field = queue[0]
    await state.update_data(field=field, queue=queue[1:])
    await state.set_state(Form.value)
    await _ask_field(message, field)


async def _ask_field(message: Message, field: str, current: str | None = None) -> None:
    text = form.prompt(field)
    if current:
        text += f"\n\nHozirgi qiymat: <code>{esc(current)}</code>"
    optional = not form.FIELDS[field].required
    await message.answer(text, reply_markup=kb.skip_kb() if optional else None)


@router.message(Form.value)
async def got_value(message: Message, state: FSMContext, db: Database, bot_username: str) -> None:
    data = await state.get_data()
    field = data["field"]
    test_id = data.get("test_id") or 0

    if field == "file":
        if message.document:
            update = {"file_kind": "document", "file_id": message.document.file_id}
        elif message.photo:
            update = {"file_kind": "photo", "file_id": message.photo[-1].file_id}
        else:
            await message.answer(t.FILE_BAD)
            return
        await message.answer(t.FILE_SAVED)
    else:
        if not message.text:
            await message.answer(form.prompt(field))
            return
        if test_id:
            test = await db.get_test(test_id)
            context = test.to_draft() if test else {}
        else:
            context = data.get("draft") or {}
        try:
            update = form.validate_text(field, message.text, context)
        except ValueError as e:
            await message.answer(str(e))
            return
        if field == "code" and await db.code_taken(update["code"], exclude_id=test_id or None):
            await message.answer(t.CODE_TAKEN.format(code=esc(update["code"])))
            return

    await apply_update(message, state, db, update, bot_username)


@router.callback_query(kb.DraftCb.filter(F.action == "skip"), Form.value)
async def skip_field(call: CallbackQuery, state: FSMContext, db: Database, bot_username: str) -> None:
    field = (await state.get_data())["field"]
    if form.FIELDS[field].required:
        await call.answer()
        return
    update = {"file_kind": None, "file_id": None} if field == "file" else {field: ""}
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    await apply_update(call.message, state, db, update, bot_username)


async def apply_update(message: Message, state: FSMContext, db: Database, update: dict, bot_username: str) -> None:
    data = await state.get_data()
    test_id = data.get("test_id") or 0

    if not test_id:
        draft = {**(data.get("draft") or {}), **update}
        await state.update_data(draft=draft)
        await ask_next(message, state, db)
        return

    # Saqlangan testni tahrirlash
    await state.clear()
    test = await db.get_test(test_id)
    if test is None:
        await message.answer(t.TEST_NOT_FOUND, reply_markup=kb.admin_menu())
        return
    await db.update_test(test_id, **update)
    if "correct_answers" in update:
        await db.recalc_results(test_id, update["correct_answers"])
    if TIME_FIELDS & update.keys() and status_of(await db.get_test(test_id)) != FINISHED:
        await db.update_test(test_id, end_notified=0)  # yangi tugash vaqtida yana xabar beriladi
    await message.answer(t.EDITED, reply_markup=kb.admin_menu())
    text, markup = await render_test(db, await db.get_test(test_id), 0)
    await message.answer(text, reply_markup=markup, disable_web_page_preview=True)


# =============== qoralamani ko'rish va saqlash ===============

def _preview_text(draft: dict) -> str:
    correct = draft.get("correct_answers") or {}
    text = t.PREVIEW.format(total=len(correct), answers=format_answers(correct) or "—")
    if all(draft.get(k) for k in TIME_FIELDS) and status_of(SimpleNamespace(**draft)) == FINISHED:
        text += "\n\n" + t.PREVIEW_PAST
    missing = form.missing_required(draft)
    if missing:
        names = ", ".join(form.FIELDS[f].label for f in missing)
        text += "\n\n" + t.PREVIEW_MISSING.format(fields=names)
    return text


async def show_preview(message: Message, state: FSMContext, db: Database, bot: Bot) -> None:
    draft = (await state.get_data()).get("draft") or {}
    await state.set_state(Form.preview)
    me = await bot.me()
    card = build_card(draft, me.username, await _channel(db))
    await send_card(bot, message.chat.id, draft, card)
    await message.answer(_preview_text(draft), reply_markup=kb.preview_kb())


@router.callback_query(kb.DraftCb.filter(F.action == "edit"))
async def draft_edit(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    if not (await state.get_data()).get("draft"):
        await call.answer(t.DRAFT_EXPIRED.format(new=t.BTN_NEW_TEST), show_alert=True)
        return
    await safe_edit(call.message, t.CHOOSE_FIELD, kb.fields_kb())
    await call.answer()


@router.callback_query(kb.DraftCb.filter(F.action == "preview"))
async def draft_back(call: CallbackQuery, state: FSMContext) -> None:
    draft = (await state.get_data()).get("draft")
    if not draft:
        await call.answer(t.DRAFT_EXPIRED.format(new=t.BTN_NEW_TEST), show_alert=True)
        return
    await state.set_state(Form.preview)
    await safe_edit(call.message, _preview_text(draft), kb.preview_kb())
    await call.answer()


@router.callback_query(kb.FieldCb.filter())
async def edit_field(call: CallbackQuery, callback_data: kb.FieldCb, state: FSMContext, db: Database) -> None:
    field = callback_data.field
    current = None
    if callback_data.test_id:
        test = await _get_test(call, db, callback_data.test_id)
        if test is None:
            return
        await state.set_data({"test_id": test.id, "field": field, "queue": []})
        if field not in ("file", "answers"):
            current = getattr(test, field)
        elif field == "answers":
            current = format_answers(test.correct_answers)
    else:
        data = await state.get_data()
        if not data.get("draft"):
            await call.answer(t.DRAFT_EXPIRED.format(new=t.BTN_NEW_TEST), show_alert=True)
            return
        await state.update_data(field=field, queue=[], test_id=0)
    await state.set_state(Form.value)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t.EDITING, reply_markup=kb.cancel_menu())
    await _ask_field(call.message, field, current)
    await call.answer()


@router.callback_query(kb.DraftCb.filter(F.action == "save"), Form.preview)
async def draft_save(call: CallbackQuery, state: FSMContext, db: Database) -> None:
    draft = (await state.get_data()).get("draft") or {}
    if form.missing_required(draft):
        await call.answer(t.PREVIEW_MISSING.format(fields=""), show_alert=True)
        return
    if await db.code_taken(draft["code"]):
        await call.answer()
        await call.message.answer(t.CODE_TAKEN.format(code=esc(draft["code"])))
        await state.update_data(field="code", queue=[], test_id=0)
        await state.set_state(Form.value)
        await _ask_field(call.message, "code")
        return

    await state.clear()
    test = await db.create_test(draft)
    await db.update_test(test.id, end_notified=int(status_of(test) == FINISHED))
    await call.message.edit_reply_markup(reply_markup=None)
    await call.answer()
    await call.message.answer(t.TEST_SAVED, reply_markup=kb.admin_menu())
    text, markup = await render_test(db, test, 0)
    await call.message.answer(text, reply_markup=markup, disable_web_page_preview=True)


@router.message(Form.preview)
async def preview_hint(message: Message) -> None:
    await message.answer(t.PREVIEW_HINT)


# =============== testlar ro'yxati va test sahifasi ===============

async def _get_test(call: CallbackQuery, db: Database, test_id: int) -> Test | None:
    test = await db.get_test(test_id)
    if test is None:
        await call.answer(t.TEST_NOT_FOUND, show_alert=True)
    return test


async def render_test(db: Database, test: Test, page: int):
    results = await db.list_results(test.id)
    text = t.TEST_VIEW.format(
        code=esc(test.code),
        title=esc(test.title),
        date=test.date,
        start=test.start_time,
        end=test.end_time,
        status=t.STATUS_TEXT[status_of(test)],
        total=len(test.correct_answers),
        count=len(results),
        hint=t.TEST_RESULTS_HINT if results else t.TEST_NO_RESULTS,
    )
    return text, kb.test_view_kb(test.id, results, page)


@router.callback_query(kb.TestCb.filter(F.action == "list"))
async def tests_list_cb(call: CallbackQuery, callback_data: kb.TestCb, db: Database) -> None:
    tests = await db.list_tests()
    if not tests:
        await safe_edit(call.message, t.NO_TESTS.format(new=t.BTN_NEW_TEST))
    else:
        statuses = {test.id: status_of(test) for test, _ in tests}
        await safe_edit(call.message, t.TESTS_TITLE, kb.tests_kb(tests, statuses, callback_data.page))
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "open"))
async def test_open(call: CallbackQuery, callback_data: kb.TestCb, state: FSMContext, db: Database) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    if await state.get_state() == Form.value.state and (await state.get_data()).get("test_id"):
        await state.clear()  # tahrirlashdan «Orqaga» bosildi
    text, markup = await render_test(db, test, callback_data.page)
    await safe_edit(call.message, text, markup)
    await call.answer()


@router.callback_query(kb.ResCb.filter())
async def result_detail(call: CallbackQuery, callback_data: kb.ResCb, db: Database) -> None:
    res = await db.get_result_by_id(callback_data.result_id)
    test = await db.get_test(res.test_id) if res else None
    if test is None:
        await call.answer(t.TEST_NOT_FOUND, show_alert=True)
        return
    ids = [r.id for r in await db.list_results(test.id)]
    rows = []
    for r in grade(test.correct_answers, res.answers):
        given = r.given or t.NO_ANSWER
        if r.is_correct:
            rows.append(t.ROW_OK.format(q=r.number, given=given))
        else:
            rows.append(t.ROW_BAD.format(q=r.number, given=given, correct=r.correct))
    text = t.RESULT_DETAIL.format(
        name=esc(res.student_name),
        code=esc(test.code),
        correct=res.correct_count,
        total=res.total,
        percent=percent(res.correct_count, res.total),
        rank=f"{ids.index(res.id) + 1} / {len(ids)}",
        time=res.submitted_at.replace("T", " "),
        rows="\n".join(rows),
    )
    await safe_edit(call.message, text, kb.result_back_kb(test.id, callback_data.page))
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "card"))
async def show_card(call: CallbackQuery, callback_data: kb.TestCb, db: Database, bot: Bot, bot_username: str) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    await call.answer()
    d = test.to_draft()
    await send_card(bot, call.message.chat.id, d, build_card(d, bot_username, await _channel(db)))


@router.callback_query(kb.TestCb.filter(F.action == "post"))
async def post_to_channel(call: CallbackQuery, callback_data: kb.TestCb, db: Database, bot: Bot, bot_username: str) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    channel = await _channel(db)
    if not channel:
        await call.answer(t.POST_NO_CHANNEL, show_alert=True)
        return
    await call.answer()
    d = test.to_draft()
    try:
        await send_card(bot, channel, d, build_card(d, bot_username, channel))
    except TelegramAPIError:
        await call.message.answer(t.POST_FAILED.format(channel=esc(channel)))
        return
    await call.message.answer(t.POSTED.format(channel=esc(channel)))


@router.callback_query(kb.TestCb.filter(F.action == "edit"))
async def edit_menu(call: CallbackQuery, callback_data: kb.TestCb, db: Database) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    await safe_edit(call.message, f"🔑 <b>{esc(test.code)}</b>\n{t.CHOOSE_FIELD}", kb.fields_kb(test.id))
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "send"))
async def send_results(call: CallbackQuery, callback_data: kb.TestCb, db: Database, bot: Bot) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    if status_of(test) != FINISHED:
        await call.answer(t.RESULTS_NOT_FINISHED, show_alert=True)
        return
    pending = [r for r in await db.list_results(test.id) if not r.result_sent]
    if not pending:
        await call.answer(t.RESULTS_NOTHING, show_alert=True)
        return
    await call.answer()
    await call.message.answer(t.RESULTS_SENDING.format(n=len(pending)))

    ok = failed = 0
    for res in pending:
        wrong_rows = [
            t.STUDENT_RESULT_WRONG_ROW.format(q=r.number, given=r.given or t.NO_ANSWER)
            for r in grade(test.correct_answers, res.answers)
            if not r.is_correct
        ]
        wrong = (
            t.STUDENT_RESULT_WRONG.format(rows="\n".join(wrong_rows))
            if wrong_rows
            else t.STUDENT_RESULT_PERFECT
        )
        try:
            await bot.send_message(
                res.student_id,
                t.STUDENT_RESULT.format(
                    code=esc(test.code),
                    title=esc(test.title),
                    correct=res.correct_count,
                    total=res.total,
                    percent=percent(res.correct_count, res.total),
                    wrong=wrong,
                ),
            )
            await db.mark_result_sent(res.id)
            ok += 1
        except TelegramAPIError:
            failed += 1
        await asyncio.sleep(0.05)  # Telegram cheklovlariga tushmaslik uchun

    await call.message.answer(
        t.RESULTS_SENT.format(ok=ok, failed=t.RESULTS_FAILED.format(n=failed) if failed else "")
    )
    text, markup = await render_test(db, test, 0)
    await call.message.answer(text, reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(kb.TestCb.filter(F.action == "del"))
async def delete_ask(call: CallbackQuery, callback_data: kb.TestCb, db: Database) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    await safe_edit(call.message, t.DELETE_CONFIRM.format(code=esc(test.code)), kb.delete_kb(test.id))
    await call.answer()


@router.callback_query(kb.TestCb.filter(F.action == "del_yes"))
async def delete_yes(call: CallbackQuery, callback_data: kb.TestCb, db: Database) -> None:
    test = await _get_test(call, db, callback_data.test_id)
    if test is None:
        return
    await db.delete_test(test.id)
    await call.answer(t.DELETED)
    tests = await db.list_tests()
    if tests:
        statuses = {x.id: status_of(x) for x, _ in tests}
        await safe_edit(call.message, t.TESTS_TITLE, kb.tests_kb(tests, statuses))
    else:
        await safe_edit(call.message, t.NO_TESTS.format(new=t.BTN_NEW_TEST))

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import texts as t
from .form import FIELDS

PAGE_SIZE = 20


# ---------- callback ma'lumotlari ----------

class NewCb(CallbackData, prefix="new"):
    action: str  # scratch | old


class TestCb(CallbackData, prefix="t"):
    # list | pick | open | card | post | edit | clone | send | del | del_yes
    action: str
    test_id: int = 0
    page: int = 0


class ResCb(CallbackData, prefix="r"):
    result_id: int
    page: int = 0


class FieldCb(CallbackData, prefix="f"):
    field: str
    test_id: int = 0  # 0 — hali saqlanmagan qoralama


class DraftCb(CallbackData, prefix="d"):
    action: str  # skip | save | edit | preview


class SetCb(CallbackData, prefix="s"):
    action: str  # channel


class AnswerCb(CallbackData, prefix="ans"):
    action: str  # yes | no


# ---------- reply menyular ----------

def admin_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=t.BTN_NEW_TEST), KeyboardButton(text=t.BTN_TESTS)],
            [KeyboardButton(text=t.BTN_SETTINGS)],
        ],
        resize_keyboard=True,
    )


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t.BTN_CANCEL)]], resize_keyboard=True)


# ---------- yordamchi ----------

def _paged(b: InlineKeyboardBuilder, items: list, page: int, add_item, make_cb) -> list[int]:
    """Sahifadagi elementlarni va sahifalash tugmalarini qo'shadi. adjust uchun o'lchamlarni qaytaradi."""
    chunk = items[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    for i, item in enumerate(chunk):
        add_item(page * PAGE_SIZE + i, item)
    sizes = [1] * len(chunk)

    pages = (len(items) + PAGE_SIZE - 1) // PAGE_SIZE
    if pages > 1:
        nav = 0
        if page > 0:
            b.button(text="◀️", callback_data=make_cb(page - 1))
            nav += 1
        b.button(text=f"{page + 1}/{pages}", callback_data=make_cb(page))
        nav += 1
        if page < pages - 1:
            b.button(text="▶️", callback_data=make_cb(page + 1))
            nav += 1
        sizes.append(nav)
    return sizes


# ---------- test yaratish ----------

def new_test_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_FROM_SCRATCH, callback_data=NewCb(action="scratch"))
    b.button(text=t.BTN_FROM_OLD, callback_data=NewCb(action="old"))
    b.adjust(1)
    return b.as_markup()


def skip_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_SKIP, callback_data=DraftCb(action="skip"))
    return b.as_markup()


def preview_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_SAVE, callback_data=DraftCb(action="save"))
    b.button(text=t.BTN_EDIT, callback_data=DraftCb(action="edit"))
    b.adjust(2)
    return b.as_markup()


def fields_kb(test_id: int = 0) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for key, spec in FIELDS.items():
        b.button(text=spec.label, callback_data=FieldCb(field=key, test_id=test_id))
    if test_id:
        b.button(text=t.BTN_BACK, callback_data=TestCb(action="open", test_id=test_id))
    else:
        b.button(text=t.BTN_BACK, callback_data=DraftCb(action="preview"))
    b.adjust(2)
    return b.as_markup()


# ---------- testlar ----------

def tests_kb(tests, statuses: dict[int, str], page: int = 0, pick: bool = False) -> InlineKeyboardMarkup:
    """pick=True — nusxa olish uchun tanlash rejimi."""
    b = InlineKeyboardBuilder()

    def add(_, item):
        test, count = item
        b.button(
            text=t.TEST_BTN.format(
                icon=t.STATUS_ICON[statuses[test.id]], code=test.code, date=test.date, count=count
            ),
            callback_data=TestCb(action="clone" if pick else "open", test_id=test.id),
        )

    sizes = _paged(b, tests, page, add, lambda p: TestCb(action="pick" if pick else "list", page=p))
    b.adjust(*sizes)
    return b.as_markup()


def test_view_kb(test_id: int, results, page: int = 0) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()

    def add(index, r):
        rank = index + 1
        b.button(
            text=t.RESULT_BTN.format(
                medal=t.MEDALS.get(rank, ""),
                rank=rank,
                mark="📨 " if r.result_sent else "",
                name=r.student_name,
                correct=r.correct_count,
                total=r.total,
            ),
            callback_data=ResCb(result_id=r.id, page=page),
        )

    sizes = _paged(b, results, page, add, lambda p: TestCb(action="open", test_id=test_id, page=p))
    if results:
        b.button(text=t.BTN_SEND_RESULTS, callback_data=TestCb(action="send", test_id=test_id))
        sizes.append(1)
    b.button(text=t.BTN_SHOW_CARD, callback_data=TestCb(action="card", test_id=test_id))
    b.button(text=t.BTN_POST_CHANNEL, callback_data=TestCb(action="post", test_id=test_id))
    b.button(text=t.BTN_EDIT, callback_data=TestCb(action="edit", test_id=test_id))
    b.button(text=t.BTN_CLONE, callback_data=TestCb(action="clone", test_id=test_id))
    b.button(text=t.BTN_DELETE, callback_data=TestCb(action="del", test_id=test_id))
    b.button(text=t.BTN_BACK, callback_data=TestCb(action="list"))
    sizes += [2, 2, 2]
    b.adjust(*sizes)
    return b.as_markup()


def open_test_kb(test_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_OPEN_RESULTS, callback_data=TestCb(action="open", test_id=test_id))
    return b.as_markup()


def result_back_kb(test_id: int, page: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_BACK, callback_data=TestCb(action="open", test_id=test_id, page=page))
    return b.as_markup()


def delete_kb(test_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_YES, callback_data=TestCb(action="del_yes", test_id=test_id))
    b.button(text=t.BTN_NO, callback_data=TestCb(action="open", test_id=test_id))
    return b.as_markup()


def settings_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_CHANGE_CHANNEL, callback_data=SetCb(action="channel"))
    return b.as_markup()


# ---------- o'quvchi ----------

def answer_confirm_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_YES, callback_data=AnswerCb(action="yes"))
    b.button(text=t.BTN_NO, callback_data=AnswerCb(action="no"))
    return b.as_markup()

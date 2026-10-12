from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from . import texts as t

PAGE_SIZE = 20


# ---------- callback ma'lumotlari ----------

class RoomCb(CallbackData, prefix="room"):
    action: str  # list | open | link | test | send | del | del_yes
    room_id: int = 0
    page: int = 0


class SubCb(CallbackData, prefix="sub"):
    sub_id: int
    page: int = 0


class TeacherCb(CallbackData, prefix="tch"):
    action: str  # ask | yes | no
    user_id: int = 0


class TestCb(CallbackData, prefix="test"):
    action: str  # done | correct_yes | correct_no


class AnswerCb(CallbackData, prefix="ans"):
    action: str  # yes | no


# ---------- asosiy menyular ----------

def main_menu(is_director: bool, is_teacher: bool) -> ReplyKeyboardMarkup | None:
    rows: list[list[KeyboardButton]] = []
    if is_director:
        rows.append([KeyboardButton(text=t.BTN_ADD_TEACHER)])
        rows.append([KeyboardButton(text=t.BTN_TEACHERS), KeyboardButton(text=t.BTN_REMOVE_TEACHER)])
    if is_director or is_teacher:
        rows.append([KeyboardButton(text=t.BTN_CREATE_ROOM), KeyboardButton(text=t.BTN_MY_ROOMS)])
    if not rows:
        return None
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True)


def cancel_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text=t.BTN_CANCEL)]], resize_keyboard=True)


# ---------- o'qituvchi ----------

def test_done_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_DONE, callback_data=TestCb(action="done"))
    return b.as_markup()


def correct_confirm_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_YES, callback_data=TestCb(action="correct_yes"))
    b.button(text=t.BTN_NO, callback_data=TestCb(action="correct_no"))
    return b.as_markup()


def _pager(b: InlineKeyboardBuilder, total: int, page: int, make_cb) -> None:
    pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    if pages <= 1:
        return
    nav = []
    if page > 0:
        nav.append(("◀️", make_cb(page - 1)))
    nav.append((f"{page + 1}/{pages}", make_cb(page)))
    if page < pages - 1:
        nav.append(("▶️", make_cb(page + 1)))
    for text, cb in nav:
        b.button(text=text, callback_data=cb)


def rooms_kb(rooms, page: int = 0) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    chunk = rooms[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    for room, count in chunk:
        b.button(
            text=t.ROOM_BTN.format(name=room.name, count=count),
            callback_data=RoomCb(action="open", room_id=room.id),
        )
    sizes = [1] * len(chunk)
    before = len(chunk)
    _pager(b, len(rooms), page, lambda p: RoomCb(action="list", page=p))
    nav_count = len(list(b.buttons)) - before
    if nav_count:
        sizes.append(nav_count)
    b.adjust(*sizes)
    return b.as_markup()


def room_kb(room_id: int, subs, page: int = 0) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    chunk = subs[page * PAGE_SIZE:(page + 1) * PAGE_SIZE]
    for s in chunk:
        b.button(
            text=t.STUDENT_BTN.format(
                mark="📨 " if s.result_sent else "",
                name=s.student_name,
                correct=s.correct_count,
                total=s.total,
            ),
            callback_data=SubCb(sub_id=s.id, page=page),
        )
    sizes = [1] * len(chunk)
    before = len(chunk)
    _pager(b, len(subs), page, lambda p: RoomCb(action="open", room_id=room_id, page=p))
    nav_count = len(list(b.buttons)) - before
    if nav_count:
        sizes.append(nav_count)

    if subs:
        b.button(text=t.BTN_SEND_RESULTS, callback_data=RoomCb(action="send", room_id=room_id))
        sizes.append(1)
    b.button(text=t.BTN_LINK, callback_data=RoomCb(action="link", room_id=room_id))
    b.button(text=t.BTN_SHOW_TEST, callback_data=RoomCb(action="test", room_id=room_id))
    b.button(text=t.BTN_DELETE_ROOM, callback_data=RoomCb(action="del", room_id=room_id))
    b.button(text=t.BTN_BACK, callback_data=RoomCb(action="list"))
    sizes += [2, 1, 1]
    b.adjust(*sizes)
    return b.as_markup()


def sub_back_kb(room_id: int, page: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_BACK, callback_data=RoomCb(action="open", room_id=room_id, page=page))
    return b.as_markup()


def room_delete_kb(room_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_YES, callback_data=RoomCb(action="del_yes", room_id=room_id))
    b.button(text=t.BTN_NO, callback_data=RoomCb(action="open", room_id=room_id))
    return b.as_markup()


# ---------- direktor ----------

def teachers_remove_kb(teachers: list[dict]) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for tch in teachers:
        b.button(
            text=f"❌ {display_name(tch)}",
            callback_data=TeacherCb(action="ask", user_id=tch["user_id"]),
        )
    b.adjust(1)
    return b.as_markup()


def teacher_remove_confirm_kb(user_id: int) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_YES, callback_data=TeacherCb(action="yes", user_id=user_id))
    b.button(text=t.BTN_NO, callback_data=TeacherCb(action="no", user_id=user_id))
    return b.as_markup()


def display_name(tch: dict) -> str:
    return tch.get("tg_name") or str(tch["user_id"])


# ---------- o'quvchi ----------

def answer_confirm_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t.BTN_YES, callback_data=AnswerCb(action="yes"))
    b.button(text=t.BTN_NO, callback_data=AnswerCb(action="no"))
    return b.as_markup()

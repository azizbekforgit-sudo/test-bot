import json
import secrets
from dataclasses import dataclass
from datetime import datetime

import aiosqlite

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    tg_name     TEXT,
    username    TEXT,
    full_name   TEXT,              -- o'quvchi o'zi kiritgan ism-familiya
    created_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    user_id     INTEGER PRIMARY KEY,
    added_by    INTEGER,
    added_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS teacher_invites (
    token       TEXT PRIMARY KEY,
    created_by  INTEGER NOT NULL,
    created_at  TEXT NOT NULL,
    used_by     INTEGER,
    used_at     TEXT
);

CREATE TABLE IF NOT EXISTS rooms (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT UNIQUE NOT NULL,
    teacher_id      INTEGER NOT NULL,
    name            TEXT NOT NULL,
    answer_example  TEXT NOT NULL,
    correct_answers TEXT NOT NULL,   -- JSON: {"1": "A", "2": "B"}
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS room_materials (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id     INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    kind        TEXT NOT NULL,       -- text | photo | document
    file_id     TEXT,
    text        TEXT
);

CREATE TABLE IF NOT EXISTS submissions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    room_id       INTEGER NOT NULL REFERENCES rooms(id) ON DELETE CASCADE,
    student_id    INTEGER NOT NULL,
    student_name  TEXT NOT NULL,
    answers       TEXT NOT NULL,     -- JSON: {"1": "A", "2": "C"}
    correct_count INTEGER NOT NULL,
    total         INTEGER NOT NULL,
    submitted_at  TEXT NOT NULL,
    result_sent   INTEGER NOT NULL DEFAULT 0,
    UNIQUE (room_id, student_id)
);
"""


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Room:
    id: int
    code: str
    teacher_id: int
    name: str
    answer_example: str
    correct_answers: dict[str, str]
    created_at: str


@dataclass
class Material:
    kind: str
    file_id: str | None
    text: str | None


@dataclass
class Submission:
    id: int
    room_id: int
    student_id: int
    student_name: str
    answers: dict[str, str]
    correct_count: int
    total: int
    submitted_at: str
    result_sent: bool


def _room(row) -> Room:
    return Room(
        id=row["id"],
        code=row["code"],
        teacher_id=row["teacher_id"],
        name=row["name"],
        answer_example=row["answer_example"],
        correct_answers=json.loads(row["correct_answers"]),
        created_at=row["created_at"],
    )


def _submission(row) -> Submission:
    return Submission(
        id=row["id"],
        room_id=row["room_id"],
        student_id=row["student_id"],
        student_name=row["student_name"],
        answers=json.loads(row["answers"]),
        correct_count=row["correct_count"],
        total=row["total"],
        submitted_at=row["submitted_at"],
        result_sent=bool(row["result_sent"]),
    )


class Database:
    def __init__(self, path: str):
        self.path = path
        self.conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.executescript(SCHEMA)
        await self.conn.commit()

    async def close(self) -> None:
        if self.conn:
            await self.conn.close()

    # ---------- foydalanuvchilar ----------

    async def upsert_user(self, user_id: int, tg_name: str, username: str | None) -> None:
        await self.conn.execute(
            """
            INSERT INTO users (user_id, tg_name, username, created_at) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET tg_name = excluded.tg_name, username = excluded.username
            """,
            (user_id, tg_name, username, _now()),
        )
        await self.conn.commit()

    async def get_full_name(self, user_id: int) -> str | None:
        cur = await self.conn.execute("SELECT full_name FROM users WHERE user_id = ?", (user_id,))
        row = await cur.fetchone()
        return row["full_name"] if row else None

    async def set_full_name(self, user_id: int, full_name: str) -> None:
        await self.conn.execute("UPDATE users SET full_name = ? WHERE user_id = ?", (full_name, user_id))
        await self.conn.commit()

    # ---------- o'qituvchilar ----------

    async def is_teacher(self, user_id: int) -> bool:
        cur = await self.conn.execute("SELECT 1 FROM teachers WHERE user_id = ?", (user_id,))
        return await cur.fetchone() is not None

    async def add_teacher(self, user_id: int, added_by: int) -> None:
        await self.conn.execute(
            "INSERT OR IGNORE INTO teachers (user_id, added_by, added_at) VALUES (?, ?, ?)",
            (user_id, added_by, _now()),
        )
        await self.conn.commit()

    async def remove_teacher(self, user_id: int) -> bool:
        cur = await self.conn.execute("DELETE FROM teachers WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return cur.rowcount > 0

    async def list_teachers(self) -> list[dict]:
        cur = await self.conn.execute(
            """
            SELECT t.user_id, t.added_at, u.tg_name, u.username,
                   (SELECT COUNT(*) FROM rooms r WHERE r.teacher_id = t.user_id) AS rooms_count
            FROM teachers t LEFT JOIN users u ON u.user_id = t.user_id
            ORDER BY t.added_at
            """
        )
        return [dict(r) for r in await cur.fetchall()]

    async def create_teacher_invite(self, created_by: int) -> str:
        token = secrets.token_urlsafe(12)
        await self.conn.execute(
            "INSERT INTO teacher_invites (token, created_by, created_at) VALUES (?, ?, ?)",
            (token, created_by, _now()),
        )
        await self.conn.commit()
        return token

    async def use_teacher_invite(self, token: str, user_id: int) -> int | None:
        """Taklifnomani ishlatadi. Muvaffaqiyatli bo'lsa direktor ID sini qaytaradi."""
        cur = await self.conn.execute(
            "SELECT created_by FROM teacher_invites WHERE token = ? AND used_by IS NULL", (token,)
        )
        row = await cur.fetchone()
        if not row:
            return None
        await self.conn.execute(
            "UPDATE teacher_invites SET used_by = ?, used_at = ? WHERE token = ?",
            (user_id, _now(), token),
        )
        await self.add_teacher(user_id, row["created_by"])
        return row["created_by"]

    # ---------- xonalar ----------

    async def create_room(
        self,
        teacher_id: int,
        name: str,
        answer_example: str,
        correct_answers: dict[str, str],
        materials: list[dict],
    ) -> Room:
        code = secrets.token_urlsafe(8)
        cur = await self.conn.execute(
            """
            INSERT INTO rooms (code, teacher_id, name, answer_example, correct_answers, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (code, teacher_id, name, answer_example, json.dumps(correct_answers), _now()),
        )
        room_id = cur.lastrowid
        await self.conn.executemany(
            "INSERT INTO room_materials (room_id, kind, file_id, text) VALUES (?, ?, ?, ?)",
            [(room_id, m["kind"], m.get("file_id"), m.get("text")) for m in materials],
        )
        await self.conn.commit()
        return await self.get_room(room_id)

    async def get_room(self, room_id: int) -> Room | None:
        cur = await self.conn.execute("SELECT * FROM rooms WHERE id = ?", (room_id,))
        row = await cur.fetchone()
        return _room(row) if row else None

    async def get_room_by_code(self, code: str) -> Room | None:
        cur = await self.conn.execute("SELECT * FROM rooms WHERE code = ?", (code,))
        row = await cur.fetchone()
        return _room(row) if row else None

    async def list_rooms(self, teacher_id: int) -> list[tuple[Room, int]]:
        cur = await self.conn.execute(
            """
            SELECT r.*, (SELECT COUNT(*) FROM submissions s WHERE s.room_id = r.id) AS cnt
            FROM rooms r WHERE r.teacher_id = ? ORDER BY r.id DESC
            """,
            (teacher_id,),
        )
        return [(_room(r), r["cnt"]) for r in await cur.fetchall()]

    async def delete_room(self, room_id: int) -> None:
        await self.conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        await self.conn.commit()

    async def get_materials(self, room_id: int) -> list[Material]:
        cur = await self.conn.execute(
            "SELECT kind, file_id, text FROM room_materials WHERE room_id = ? ORDER BY id", (room_id,)
        )
        return [Material(r["kind"], r["file_id"], r["text"]) for r in await cur.fetchall()]

    # ---------- javoblar ----------

    async def get_submission(self, room_id: int, student_id: int) -> Submission | None:
        cur = await self.conn.execute(
            "SELECT * FROM submissions WHERE room_id = ? AND student_id = ?", (room_id, student_id)
        )
        row = await cur.fetchone()
        return _submission(row) if row else None

    async def get_submission_by_id(self, submission_id: int) -> Submission | None:
        cur = await self.conn.execute("SELECT * FROM submissions WHERE id = ?", (submission_id,))
        row = await cur.fetchone()
        return _submission(row) if row else None

    async def add_submission(
        self,
        room_id: int,
        student_id: int,
        student_name: str,
        answers: dict[str, str],
        correct_count: int,
        total: int,
    ) -> bool:
        """Javobni saqlaydi. O'quvchi avval topshirgan bo'lsa False qaytaradi."""
        cur = await self.conn.execute(
            """
            INSERT OR IGNORE INTO submissions
                (room_id, student_id, student_name, answers, correct_count, total, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (room_id, student_id, student_name, json.dumps(answers), correct_count, total, _now()),
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def list_submissions(self, room_id: int) -> list[Submission]:
        cur = await self.conn.execute(
            "SELECT * FROM submissions WHERE room_id = ? ORDER BY correct_count DESC, submitted_at",
            (room_id,),
        )
        return [_submission(r) for r in await cur.fetchall()]

    async def mark_result_sent(self, submission_id: int) -> None:
        await self.conn.execute("UPDATE submissions SET result_sent = 1 WHERE id = ?", (submission_id,))
        await self.conn.commit()


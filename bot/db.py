import json
from dataclasses import dataclass
from datetime import datetime

import aiosqlite

from .answers import count_correct

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     INTEGER PRIMARY KEY,
    tg_name     TEXT,
    username    TEXT,
    full_name   TEXT,              -- o'quvchi o'zi kiritgan ism-familiya
    created_at  TEXT NOT NULL
);

-- Bir marta kiritiladigan sozlamalar (kanal havolasi va h.k.)
CREATE TABLE IF NOT EXISTS settings (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT NOT NULL UNIQUE COLLATE NOCASE,
    title           TEXT NOT NULL,
    subject         TEXT NOT NULL DEFAULT '',
    hashtags        TEXT NOT NULL DEFAULT '',
    subtitle        TEXT NOT NULL DEFAULT '',
    footer          TEXT NOT NULL DEFAULT '',
    date            TEXT NOT NULL,     -- KK.OO.YYYY
    start_time      TEXT NOT NULL,     -- SS:DD
    end_time        TEXT NOT NULL,     -- SS:DD
    file_kind       TEXT,              -- document | photo | NULL
    file_id         TEXT,
    correct_answers TEXT NOT NULL,     -- JSON: {"1": "A", "2": "B"}
    end_notified    INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS test_results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id       INTEGER NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    student_id    INTEGER NOT NULL,
    student_name  TEXT NOT NULL,
    answers       TEXT NOT NULL,     -- JSON: {"1": "A", "2": "C"}
    correct_count INTEGER NOT NULL,
    total         INTEGER NOT NULL,
    submitted_at  TEXT NOT NULL,
    result_sent   INTEGER NOT NULL DEFAULT 0,
    UNIQUE (test_id, student_id)
);
"""

# Testning foydalanuvchi tahrirlay oladigan maydonlari
TEST_FIELDS = (
    "code", "title", "subject", "hashtags", "subtitle", "footer",
    "date", "start_time", "end_time", "file_kind", "file_id", "correct_answers",
)


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


@dataclass
class Test:
    id: int
    code: str
    title: str
    subject: str
    hashtags: str
    subtitle: str
    footer: str
    date: str
    start_time: str
    end_time: str
    file_kind: str | None
    file_id: str | None
    correct_answers: dict[str, str]
    end_notified: bool
    created_at: str

    def to_draft(self) -> dict:
        return {f: getattr(self, f) for f in TEST_FIELDS}


@dataclass
class Result:
    id: int
    test_id: int
    student_id: int
    student_name: str
    answers: dict[str, str]
    correct_count: int
    total: int
    submitted_at: str
    result_sent: bool


def _test(row) -> Test:
    d = dict(row)
    d["correct_answers"] = json.loads(d["correct_answers"])
    d["end_notified"] = bool(d["end_notified"])
    return Test(**d)


def _result(row) -> Result:
    d = dict(row)
    d["answers"] = json.loads(d["answers"])
    d["result_sent"] = bool(d["result_sent"])
    return Result(**d)


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
        await self.conn.execute(
            """
            INSERT INTO users (user_id, full_name, created_at) VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET full_name = excluded.full_name
            """,
            (user_id, full_name, _now()),
        )
        await self.conn.commit()

    # ---------- sozlamalar ----------

    async def get_setting(self, key: str) -> str | None:
        cur = await self.conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = await cur.fetchone()
        return row["value"] if row else None

    async def set_setting(self, key: str, value: str) -> None:
        await self.conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        await self.conn.commit()

    # ---------- testlar ----------

    async def create_test(self, draft: dict) -> Test:
        values = {f: draft.get(f) for f in TEST_FIELDS}
        values["correct_answers"] = json.dumps(values["correct_answers"])
        for f in ("subject", "hashtags", "subtitle", "footer"):
            values[f] = values[f] or ""
        cols = ", ".join(values)
        marks = ", ".join("?" for _ in values)
        cur = await self.conn.execute(
            f"INSERT INTO tests ({cols}, created_at) VALUES ({marks}, ?)",
            (*values.values(), _now()),
        )
        await self.conn.commit()
        return await self.get_test(cur.lastrowid)

    async def update_test(self, test_id: int, **fields) -> None:
        assert set(fields) <= set(TEST_FIELDS) | {"end_notified"}
        if "correct_answers" in fields:
            fields["correct_answers"] = json.dumps(fields["correct_answers"])
        sets = ", ".join(f"{k} = ?" for k in fields)
        await self.conn.execute(f"UPDATE tests SET {sets} WHERE id = ?", (*fields.values(), test_id))
        await self.conn.commit()

    async def get_test(self, test_id: int) -> Test | None:
        cur = await self.conn.execute("SELECT * FROM tests WHERE id = ?", (test_id,))
        row = await cur.fetchone()
        return _test(row) if row else None

    async def get_test_by_code(self, code: str) -> Test | None:
        cur = await self.conn.execute("SELECT * FROM tests WHERE code = ?", (code.strip(),))
        row = await cur.fetchone()
        return _test(row) if row else None

    async def code_taken(self, code: str, exclude_id: int | None = None) -> bool:
        cur = await self.conn.execute(
            "SELECT 1 FROM tests WHERE code = ? AND id != ?", (code, exclude_id or 0)
        )
        return await cur.fetchone() is not None

    async def list_tests(self) -> list[tuple[Test, int]]:
        cur = await self.conn.execute(
            """
            SELECT t.*, (SELECT COUNT(*) FROM test_results r WHERE r.test_id = t.id) AS cnt
            FROM tests t ORDER BY t.id DESC
            """
        )
        rows = await cur.fetchall()
        return [(_test({k: r[k] for k in r.keys() if k != "cnt"}), r["cnt"]) for r in rows]

    async def unnotified_tests(self) -> list[Test]:
        cur = await self.conn.execute("SELECT * FROM tests WHERE end_notified = 0")
        return [_test(r) for r in await cur.fetchall()]

    async def delete_test(self, test_id: int) -> None:
        await self.conn.execute("DELETE FROM tests WHERE id = ?", (test_id,))
        await self.conn.commit()

    async def recalc_results(self, test_id: int, correct: dict[str, str]) -> None:
        """To'g'ri javoblar o'zgartirilganda barcha natijalarni qayta hisoblaydi."""
        for r in await self.list_results(test_id):
            await self.conn.execute(
                "UPDATE test_results SET correct_count = ?, total = ? WHERE id = ?",
                (count_correct(correct, r.answers), len(correct), r.id),
            )
        await self.conn.commit()

    # ---------- natijalar ----------

    async def get_result(self, test_id: int, student_id: int) -> Result | None:
        cur = await self.conn.execute(
            "SELECT * FROM test_results WHERE test_id = ? AND student_id = ?", (test_id, student_id)
        )
        row = await cur.fetchone()
        return _result(row) if row else None

    async def get_result_by_id(self, result_id: int) -> Result | None:
        cur = await self.conn.execute("SELECT * FROM test_results WHERE id = ?", (result_id,))
        row = await cur.fetchone()
        return _result(row) if row else None

    async def add_result(
        self,
        test_id: int,
        student_id: int,
        student_name: str,
        answers: dict[str, str],
        correct_count: int,
        total: int,
    ) -> bool:
        """Javobni saqlaydi. O'quvchi avval topshirgan bo'lsa False qaytaradi."""
        cur = await self.conn.execute(
            """
            INSERT OR IGNORE INTO test_results
                (test_id, student_id, student_name, answers, correct_count, total, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (test_id, student_id, student_name, json.dumps(answers), correct_count, total, _now()),
        )
        await self.conn.commit()
        return cur.rowcount > 0

    async def list_results(self, test_id: int) -> list[Result]:
        """Natijalar: eng ko'p to'g'ri javob berganidan eng kamiga qarab tartiblangan."""
        cur = await self.conn.execute(
            "SELECT * FROM test_results WHERE test_id = ? ORDER BY correct_count DESC, submitted_at",
            (test_id,),
        )
        return [_result(r) for r in await cur.fetchall()]

    async def mark_result_sent(self, result_id: int) -> None:
        await self.conn.execute("UPDATE test_results SET result_sent = 1 WHERE id = ?", (result_id,))
        await self.conn.commit()

"""Ma'lumotlar bazasi.

DATABASE_URL berilgan bo'lsa — PostgreSQL (serverda, masalan Neon/Render),
aks holda — SQLite fayli (kompyuterda ishga tushirish uchun).
"""

import json
import re
from dataclasses import dataclass

from . import timeutils
from .answers import count_correct

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,
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
    id              {ID},
    code            TEXT NOT NULL,
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

-- Test kodi takrorlanmas va katta-kichik harfga sezgir emas
CREATE UNIQUE INDEX IF NOT EXISTS tests_code_uniq ON tests (lower(code));

CREATE TABLE IF NOT EXISTS test_results (
    id            {ID},
    test_id       BIGINT NOT NULL REFERENCES tests(id) ON DELETE CASCADE,
    student_id    BIGINT NOT NULL,
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
    return timeutils.now().strftime("%Y-%m-%d %H:%M:%S")


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


_TEST_COLS = ("id", "created_at", "end_notified", *TEST_FIELDS)


def _test(row) -> Test:
    d = {k: row[k] for k in _TEST_COLS}
    d["correct_answers"] = json.loads(d["correct_answers"])
    d["end_notified"] = bool(d["end_notified"])
    return Test(**d)


def _result(row) -> Result:
    d = dict(row)
    d["answers"] = json.loads(d["answers"])
    d["result_sent"] = bool(d["result_sent"])
    return Result(**d)


# ---------- SQLite / PostgreSQL uchun bir xil interfeys ----------

class _SQLite:
    id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"

    def __init__(self, path: str):
        self.path = path

    async def connect(self, schema: str) -> None:
        import aiosqlite

        self.conn = await aiosqlite.connect(self.path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA foreign_keys = ON")
        await self.conn.executescript(schema)
        await self.conn.commit()

    async def close(self) -> None:
        await self.conn.close()

    async def execute(self, sql: str, *args) -> int:
        cur = await self.conn.execute(sql, args)
        await self.conn.commit()
        return cur.rowcount

    async def insert(self, sql: str, *args) -> int:
        cur = await self.conn.execute(sql, args)
        await self.conn.commit()
        return cur.lastrowid

    async def fetchone(self, sql: str, *args):
        cur = await self.conn.execute(sql, args)
        return await cur.fetchone()

    async def fetchall(self, sql: str, *args):
        cur = await self.conn.execute(sql, args)
        return await cur.fetchall()


class _Postgres:
    id_type = "BIGSERIAL PRIMARY KEY"

    def __init__(self, url: str):
        self.url = url

    @staticmethod
    def _sql(sql: str) -> str:
        # "?" belgilarini PostgreSQL uslubidagi $1, $2 ... ga almashtiramiz
        parts = sql.split("?")
        return parts[0] + "".join(f"${i}{p}" for i, p in enumerate(parts[1:], 1))

    async def connect(self, schema: str) -> None:
        import asyncpg

        # asyncpg "channel_binding" parametrini tushunmaydi (Neon havolasida bo'ladi) — olib tashlaymiz.
        # statement_cache_size=0 — pgbouncer (pooler) orqali ulanganda ham ishlashi uchun.
        url = re.sub(r"[?&]channel_binding=[^&]*", "", self.url).replace("&&", "&")
        if "?" not in url and "&" in url:
            url = url.replace("&", "?", 1)
        self.pool = await asyncpg.create_pool(url, min_size=1, max_size=5, statement_cache_size=0)
        async with self.pool.acquire() as conn:
            await conn.execute(schema)

    async def close(self) -> None:
        await self.pool.close()

    async def execute(self, sql: str, *args) -> int:
        status = await self.pool.execute(self._sql(sql), *args)  # masalan "INSERT 0 1"
        try:
            return int(status.split()[-1])
        except ValueError:
            return 0

    async def insert(self, sql: str, *args) -> int:
        return await self.pool.fetchval(self._sql(sql) + " RETURNING id", *args)

    async def fetchone(self, sql: str, *args):
        return await self.pool.fetchrow(self._sql(sql), *args)

    async def fetchall(self, sql: str, *args):
        return await self.pool.fetch(self._sql(sql), *args)


class Database:
    def __init__(self, path: str, url: str | None = None):
        self.backend = _Postgres(url) if url else _SQLite(path)

    async def connect(self) -> None:
        await self.backend.connect(SCHEMA.replace("{ID}", self.backend.id_type))

    async def close(self) -> None:
        await self.backend.close()

    # ---------- foydalanuvchilar ----------

    async def upsert_user(self, user_id: int, tg_name: str, username: str | None) -> None:
        await self.backend.execute(
            """
            INSERT INTO users (user_id, tg_name, username, created_at) VALUES (?, ?, ?, ?)
            ON CONFLICT (user_id) DO UPDATE SET tg_name = excluded.tg_name, username = excluded.username
            """,
            user_id, tg_name, username, _now(),
        )

    async def get_full_name(self, user_id: int) -> str | None:
        row = await self.backend.fetchone("SELECT full_name FROM users WHERE user_id = ?", user_id)
        return row["full_name"] if row else None

    async def set_full_name(self, user_id: int, full_name: str) -> None:
        await self.backend.execute(
            """
            INSERT INTO users (user_id, full_name, created_at) VALUES (?, ?, ?)
            ON CONFLICT (user_id) DO UPDATE SET full_name = excluded.full_name
            """,
            user_id, full_name, _now(),
        )

    # ---------- sozlamalar ----------

    async def get_setting(self, key: str) -> str | None:
        row = await self.backend.fetchone("SELECT value FROM settings WHERE key = ?", key)
        return row["value"] if row else None

    async def set_setting(self, key: str, value: str) -> None:
        await self.backend.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT (key) DO UPDATE SET value = excluded.value",
            key, value,
        )

    # ---------- testlar ----------

    async def create_test(self, draft: dict) -> Test:
        values = {f: draft.get(f) for f in TEST_FIELDS}
        values["correct_answers"] = json.dumps(values["correct_answers"])
        for f in ("subject", "hashtags", "subtitle", "footer"):
            values[f] = values[f] or ""
        cols = ", ".join(values)
        marks = ", ".join("?" for _ in values)
        test_id = await self.backend.insert(
            f"INSERT INTO tests ({cols}, created_at) VALUES ({marks}, ?)",
            *values.values(), _now(),
        )
        return await self.get_test(test_id)

    async def update_test(self, test_id: int, **fields) -> None:
        assert set(fields) <= set(TEST_FIELDS) | {"end_notified"}
        if "correct_answers" in fields:
            fields["correct_answers"] = json.dumps(fields["correct_answers"])
        if "end_notified" in fields:
            fields["end_notified"] = int(fields["end_notified"])
        sets = ", ".join(f"{k} = ?" for k in fields)
        await self.backend.execute(f"UPDATE tests SET {sets} WHERE id = ?", *fields.values(), test_id)

    async def get_test(self, test_id: int) -> Test | None:
        row = await self.backend.fetchone("SELECT * FROM tests WHERE id = ?", test_id)
        return _test(row) if row else None

    async def get_test_by_code(self, code: str) -> Test | None:
        row = await self.backend.fetchone(
            "SELECT * FROM tests WHERE lower(code) = lower(?)", code.strip()
        )
        return _test(row) if row else None

    async def code_taken(self, code: str, exclude_id: int | None = None) -> bool:
        row = await self.backend.fetchone(
            "SELECT 1 AS x FROM tests WHERE lower(code) = lower(?) AND id != ?", code, exclude_id or 0
        )
        return row is not None

    async def list_tests(self) -> list[tuple[Test, int]]:
        rows = await self.backend.fetchall(
            """
            SELECT t.*, (SELECT COUNT(*) FROM test_results r WHERE r.test_id = t.id) AS cnt
            FROM tests t ORDER BY t.id DESC
            """
        )
        return [(_test(r), int(r["cnt"])) for r in rows]

    async def unnotified_tests(self) -> list[Test]:
        return [_test(r) for r in await self.backend.fetchall("SELECT * FROM tests WHERE end_notified = 0")]

    async def delete_test(self, test_id: int) -> None:
        await self.backend.execute("DELETE FROM tests WHERE id = ?", test_id)

    async def recalc_results(self, test_id: int, correct: dict[str, str]) -> None:
        """To'g'ri javoblar o'zgartirilganda barcha natijalarni qayta hisoblaydi."""
        for r in await self.list_results(test_id):
            await self.backend.execute(
                "UPDATE test_results SET correct_count = ?, total = ? WHERE id = ?",
                count_correct(correct, r.answers), len(correct), r.id,
            )

    # ---------- natijalar ----------

    async def get_result(self, test_id: int, student_id: int) -> Result | None:
        row = await self.backend.fetchone(
            "SELECT * FROM test_results WHERE test_id = ? AND student_id = ?", test_id, student_id
        )
        return _result(row) if row else None

    async def get_result_by_id(self, result_id: int) -> Result | None:
        row = await self.backend.fetchone("SELECT * FROM test_results WHERE id = ?", result_id)
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
        inserted = await self.backend.execute(
            """
            INSERT INTO test_results
                (test_id, student_id, student_name, answers, correct_count, total, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (test_id, student_id) DO NOTHING
            """,
            test_id, student_id, student_name, json.dumps(answers), correct_count, total, _now(),
        )
        return inserted > 0

    async def list_results(self, test_id: int) -> list[Result]:
        """Natijalar: eng ko'p to'g'ri javob berganidan eng kamiga qarab tartiblangan."""
        rows = await self.backend.fetchall(
            "SELECT * FROM test_results WHERE test_id = ? ORDER BY correct_count DESC, submitted_at, id",
            test_id,
        )
        return [_result(r) for r in rows]

    async def mark_result_sent(self, result_id: int) -> None:
        await self.backend.execute("UPDATE test_results SET result_sent = 1 WHERE id = ?", result_id)

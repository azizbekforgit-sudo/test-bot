"""Javoblarni matndan ajratib olish va tekshirish."""

import re
from dataclasses import dataclass

# "1A", "1 A", "1-A", "1.A", "1)A", "1:A", "1=A" — hammasi qabul qilinadi.
# Raqamdan keyin bitta harf (lotin yoki kirill) keladi.
ANSWER_RE = re.compile(r"(\d{1,3})\s*[-.):=]?\s*([^\W\d_])(?![^\W\d_])")

# Kirill harflari lotincha ko'rinishdagi harfga aylantiriladi:
# o'quvchi "1А 2Б 3С" yozsa ham, o'qituvchi "1 A 2 B 3 C" yozsa ham bir xil bo'ladi.
CYR_TO_LAT = str.maketrans({
    "А": "A",
    "Б": "B",
    "С": "C",
    "Д": "D",
    "Е": "E",
})


def normalize_letter(letter: str) -> str:
    return letter.upper().translate(CYR_TO_LAT)


def parse_answers(text: str) -> dict[str, str]:
    """Matndan {savol_raqami: javob} lug'atini qaytaradi (raqam bo'yicha tartiblangan)."""
    result: dict[int, str] = {}
    for num, letter in ANSWER_RE.findall(text or ""):
        n = int(num)
        if n > 0:
            result[n] = normalize_letter(letter)
    return {str(k): result[k] for k in sorted(result)}


def format_answers(answers: dict[str, str]) -> str:
    return ", ".join(f"{q}{a}" for q, a in answers.items())


@dataclass
class QuestionResult:
    number: str
    correct: str
    given: str | None

    @property
    def is_correct(self) -> bool:
        return self.given == self.correct


def grade(correct: dict[str, str], given: dict[str, str]) -> list[QuestionResult]:
    return [QuestionResult(q, a, given.get(q)) for q, a in correct.items()]


def count_correct(correct: dict[str, str], given: dict[str, str]) -> int:
    return sum(r.is_correct for r in grade(correct, given))

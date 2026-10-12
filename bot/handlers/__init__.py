from aiogram import Router

from . import common, director, student, teacher


def get_routers() -> list[Router]:
    # Tartib muhim: common (/start va bekor qilish) birinchi bo'lishi kerak
    return [common.router, director.router, teacher.router, student.router]

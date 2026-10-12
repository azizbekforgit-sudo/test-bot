from aiogram import Router

from . import admin, common, student


def get_routers() -> list[Router]:
    # Tartib muhim: common (/start va bekor qilish) birinchi, o'quvchi — oxirida
    return [common.router, admin.router, student.router]

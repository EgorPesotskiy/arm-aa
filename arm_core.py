# -*- coding: utf-8 -*-
"""Фрагменты модулей программного комплекса «АРМ администратора автосалона».

Модуль М1 — авторизация пользователей (блокировка после 5 неверных попыток).
Модуль М2 — учёт парка автомобилей (проверка VIN, статусы автомобиля).
"""
import re

# VIN: ровно 17 символов, латинские буквы и цифры, буквы I, O, Q запрещены
VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")

# число неверных попыток входа до блокировки учётной записи (требование ТЗ)
MAX_ATTEMPTS = 5

STATUSES = ("в пути", "на складе", "в резерве", "на тест-драйве",
            "продан", "снят с продажи")

# допустимые переходы статусов: из какого статуса -> в какие можно перейти
TRANSITIONS = {
    "в пути": {"на складе", "снят с продажи"},
    "на складе": {"в резерве", "на тест-драйве", "продан", "снят с продажи"},
    "в резерве": {"на складе", "продан"},
    "на тест-драйве": {"на складе", "в резерве"},
    "продан": set(),                      # конечный статус
    "снят с продажи": {"на складе"},
}


class AccountLocked(Exception):
    """Учётная запись заблокирована после MAX_ATTEMPTS неверных попыток."""


def validate_vin(vin: str) -> bool:
    """Проверить формат идентификационного номера VIN.

    Пробелы по краям отбрасываются, регистр не важен.
    """
    if not isinstance(vin, str):
        return False
    return bool(VIN_RE.match(vin.strip().upper()))


def change_status(current: str, new: str) -> str:
    """Сменить статус автомобиля с контролем допустимых переходов.

    Возвращает новый статус или возбуждает ValueError.
    """
    if current not in STATUSES or new not in STATUSES:
        raise ValueError(f"неизвестный статус: {current!r} -> {new!r}")
    if new not in TRANSITIONS[current]:
        raise ValueError(f"недопустимый переход: {current} -> {new}")
    return new


class AuthService:
    """Авторизация с блокировкой учётной записи после 5 неверных попыток."""

    def __init__(self, users: dict):
        self._users = dict(users)   # логин -> пароль
        self._fails = {}            # логин -> число неверных попыток подряд
        self._locked = set()        # заблокированные логины

    def login(self, user: str, password: str) -> bool:
        """Вернуть True при успешном входе; при блокировке — AccountLocked."""
        if user in self._locked:
            raise AccountLocked(user)
        if self._users.get(user) == password:
            self._fails[user] = 0   # успешный вход сбрасывает счётчик
            return True
        self._fails[user] = self._fails.get(user, 0) + 1
        if self._fails[user] >= MAX_ATTEMPTS:
            self._locked.add(user)
        return False

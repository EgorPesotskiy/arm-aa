# -*- coding: utf-8 -*-
"""Фрагменты модулей программного комплекса «АРМ администратора автосалона».

Модуль М1 — авторизация пользователей (блокировка после 5 неверных попыток).
Модуль М2 — учёт парка автомобилей (проверка VIN, статусы, реестр автомобилей).
"""
import re
from dataclasses import dataclass, field

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


def normalize_vin(vin: str) -> str:
    """Привести VIN к каноническому виду: без пробелов по краям, в верхнем регистре."""
    return vin.strip().upper()


def validate_vin(vin: str) -> bool:
    """Проверить формат идентификационного номера VIN (регистр не важен)."""
    if not isinstance(vin, str):
        return False
    return bool(VIN_RE.match(normalize_vin(vin)))


def change_status(current: str, new: str) -> str:
    """Сменить статус автомобиля с контролем допустимых переходов.

    Возвращает новый статус или возбуждает ValueError.
    """
    if current not in STATUSES or new not in STATUSES:
        raise ValueError(f"неизвестный статус: {current!r} -> {new!r}")
    if new not in TRANSITIONS[current]:
        raise ValueError(f"недопустимый переход: {current} -> {new}")
    return new


@dataclass
class Car:
    """Карточка автомобиля с историей смены статусов."""
    vin: str
    model: str
    price: int
    status: str = "в пути"
    history: list = field(default_factory=list)

    def set_status(self, new: str) -> None:
        """Сменить статус с проверкой перехода и записью в историю."""
        self.status, old = change_status(self.status, new), self.status
        self.history.append((old, new))


class CarRegistry:
    """Реестр автомобилей с индексом по VIN.

    Оптимизация по сравнению с v2: поиск по VIN выполняется через словарь
    за O(1) вместо перебора списка, уникальность VIN контролируется при добавлении.
    """

    def __init__(self):
        self._by_vin = {}

    def add(self, car: Car) -> Car:
        if not validate_vin(car.vin):
            raise ValueError(f"неверный VIN: {car.vin!r}")
        if car.price <= 0:
            raise ValueError("цена должна быть положительной")
        car.vin = normalize_vin(car.vin)
        if car.vin in self._by_vin:
            raise ValueError(f"VIN {car.vin} уже есть в реестре")
        self._by_vin[car.vin] = car
        return car

    def find(self, vin: str):
        """Найти автомобиль по VIN или вернуть None."""
        return self._by_vin.get(normalize_vin(vin))

    def by_status(self, status: str) -> list:
        return [c for c in self._by_vin.values() if c.status == status]

    def __len__(self):
        return len(self._by_vin)


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

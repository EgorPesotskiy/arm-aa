# -*- coding: utf-8 -*-
"""Модульные тесты модулей М1 и М2 (позитивные — уровень MAT, вместе с негативными — AT)."""
import pytest

from arm_core import (AccountLocked, AuthService, Car, CarRegistry, change_status,
                      validate_vin)


# ---------- М2: проверка VIN ----------
@pytest.mark.parametrize("vin", [
    "XTA21099071234567",      # ВАЗ
    "WVWZZZ1KZAW123456",      # Volkswagen
    "xta21099071234567",      # нижний регистр приводится к верхнему
])
def test_vin_valid(vin):
    assert validate_vin(vin)


@pytest.mark.parametrize("vin", [
    "",                       # пустое значение
    "XTA2109907123456",       # 16 символов (граница - 1)
    "XTA210990712345678",     # 18 символов (граница + 1)
    "XTA21099O71234567",      # недопустимая буква O
    "XTA-1099071234567",      # спецсимвол
    None,                     # не строка
])
def test_vin_invalid(vin):
    assert not validate_vin(vin)


# ---------- М2: статусы автомобиля ----------
def test_status_stock_to_reserve():
    assert change_status("на складе", "в резерве") == "в резерве"


def test_status_sold_is_final():
    with pytest.raises(ValueError):
        change_status("продан", "на складе")


def test_status_unknown():
    with pytest.raises(ValueError):
        change_status("на складе", "угнан")


# ---------- М2: реестр автомобилей ----------
@pytest.fixture
def registry():
    reg = CarRegistry()
    reg.add(Car("XTA21099071234567", "Lada Vesta", 1_450_000))
    return reg


def test_registry_find_case_insensitive(registry):
    assert registry.find(" xta21099071234567 ").model == "Lada Vesta"


def test_registry_duplicate_vin(registry):
    with pytest.raises(ValueError):
        registry.add(Car("XTA21099071234567", "Lada Granta", 900_000))


def test_registry_bad_price(registry):
    with pytest.raises(ValueError):
        registry.add(Car("WVWZZZ1KZAW123456", "VW Polo", 0))


def test_car_status_history(registry):
    car = registry.find("XTA21099071234567")
    car.set_status("на складе")
    car.set_status("в резерве")
    assert car.history == [("в пути", "на складе"), ("на складе", "в резерве")]
    assert registry.by_status("в резерве") == [car]


# ---------- М1: авторизация ----------
@pytest.fixture
def auth():
    return AuthService({"admin": "Adm!n2026", "manager": "Mgr#2026"})


def test_login_ok(auth):
    assert auth.login("admin", "Adm!n2026")


def test_lock_after_five_attempts(auth):
    for _ in range(5):
        assert not auth.login("manager", "bad")
    with pytest.raises(AccountLocked):
        auth.login("manager", "Mgr#2026")


def test_four_attempts_do_not_lock(auth):
    for _ in range(4):
        auth.login("manager", "bad")
    assert auth.login("manager", "Mgr#2026")

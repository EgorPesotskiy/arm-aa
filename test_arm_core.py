import pytest

from arm_core import AccountLocked, AuthService, change_status, validate_vin


def test_vin_valid():
    assert validate_vin("XTA21099071234567")


def test_vin_invalid():
    assert not validate_vin("XTA2109907123456")


def test_status_stock_to_reserve():
    assert change_status("на складе", "в резерве") == "в резерве"


def test_lock_after_five_attempts():
    auth = AuthService({"manager": "Mgr#2026"})
    for _ in range(5):
        auth.login("manager", "bad")
    with pytest.raises(AccountLocked):
        auth.login("manager", "Mgr#2026")

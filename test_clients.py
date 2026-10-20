# -*- coding: utf-8 -*-
import pytest

from clients import Client, normalize_phone, validate_inn


@pytest.mark.parametrize("inn", ["7707083893", "500100732259"])
def test_inn_valid(inn):
    assert validate_inn(inn)


@pytest.mark.parametrize("inn", ["7707083894", "77070838", "50010073225X", ""])
def test_inn_invalid(inn):
    assert not validate_inn(inn)


@pytest.mark.parametrize("raw", ["8 (918) 123-45-67", "+7 918 123 45 67", "9181234567"])
def test_phone_normalized(raw):
    assert normalize_phone(raw) == "+79181234567"


def test_phone_invalid():
    with pytest.raises(ValueError):
        normalize_phone("123-45")


def test_client_requires_consent():
    with pytest.raises(ValueError):
        Client("Иванов И. И.", "89181234567")


def test_client_ok():
    c = Client("Иванов И. И.", "8 918 123-45-67", inn="500100732259", pd_consent=True)
    assert c.phone == "+79181234567"

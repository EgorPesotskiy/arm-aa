# -*- coding: utf-8 -*-
import pytest

from arm_core import Car, CarRegistry
from reports import format_report, stock_report, stock_value


@pytest.fixture
def registry():
    reg = CarRegistry()
    a = reg.add(Car("XTA21099071234567", "Lada Vesta", 1_450_000))
    b = reg.add(Car("WVWZZZ1KZAW123456", "VW Polo", 1_900_000))
    a.set_status("на складе")
    b.set_status("на складе")
    b.set_status("продан")
    return reg


def test_stock_report(registry):
    rep = stock_report(registry)
    assert rep["на складе"] == 1 and rep["продан"] == 1 and rep["в пути"] == 0


def test_stock_value_excludes_sold(registry):
    assert stock_value(registry) == 1_450_000


def test_format_report(registry):
    assert "Стоимость склада: 1 450 000 руб." in format_report(registry)

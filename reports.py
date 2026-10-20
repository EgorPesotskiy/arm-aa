# -*- coding: utf-8 -*-
"""Отчёты АРМ-АА: остатки автомобилей по статусам и стоимость склада."""
from collections import Counter

from arm_core import STATUSES, CarRegistry


def stock_report(registry: CarRegistry) -> dict:
    """Количество автомобилей в каждом статусе (все статусы, включая нулевые)."""
    counts = Counter(car.status for car in registry._by_vin.values())
    return {status: counts.get(status, 0) for status in STATUSES}


def stock_value(registry: CarRegistry) -> int:
    """Суммарная цена автомобилей, которые ещё не проданы и не сняты с продажи."""
    return sum(car.price for car in registry._by_vin.values()
               if car.status not in ("продан", "снят с продажи"))


def format_report(registry: CarRegistry) -> str:
    """Текстовый отчёт для вывода на экран или печати."""
    lines = ["Остатки автомобилей по статусам:"]
    for status, n in stock_report(registry).items():
        lines.append(f"  {status:<16}{n:>5}")
    lines.append(f"Стоимость склада: {stock_value(registry):,} руб.".replace(",", " "))
    return "\n".join(lines)

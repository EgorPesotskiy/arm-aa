# -*- coding: utf-8 -*-
"""Модуль М3 «Клиентская база»: проверка ИНН и телефона, карточка клиента."""
import re
from dataclasses import dataclass

# весовые коэффициенты контрольных разрядов ИНН
_W10 = (2, 4, 10, 3, 5, 9, 4, 6, 8)
_W11 = (7, 2, 4, 10, 3, 5, 9, 4, 6, 8)
_W12 = (3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8)


def _check_digit(digits, weights) -> int:
    return sum(d * w for d, w in zip(digits, weights)) % 11 % 10


def validate_inn(inn: str) -> bool:
    """ИНН юрлица — 10 цифр, физлица — 12 цифр; проверяются контрольные разряды."""
    if not (isinstance(inn, str) and inn.isdigit() and len(inn) in (10, 12)):
        return False
    d = [int(c) for c in inn]
    if len(d) == 10:
        return d[9] == _check_digit(d, _W10)
    return d[10] == _check_digit(d, _W11) and d[11] == _check_digit(d, _W12)


def normalize_phone(phone: str) -> str:
    """Привести российский номер к виду +7XXXXXXXXXX или возбудить ValueError."""
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 11 and digits[0] in "78":
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError(f"неверный номер телефона: {phone!r}")
    return "+7" + digits


@dataclass
class Client:
    """Карточка клиента; без согласия на обработку ПДн создать нельзя (152-ФЗ)."""
    name: str
    phone: str
    inn: str = ""
    pd_consent: bool = False

    def __post_init__(self):
        if not self.pd_consent:
            raise ValueError("нет согласия на обработку персональных данных")
        if self.inn and not validate_inn(self.inn):
            raise ValueError(f"неверный ИНН: {self.inn}")
        self.phone = normalize_phone(self.phone)

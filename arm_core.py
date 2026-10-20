import re

VIN_RE = re.compile(r"^[A-HJ-NPR-Z0-9]{17}$")
MAX_ATTEMPTS = 5

STATUSES = ("в пути", "на складе", "в резерве", "на тест-драйве",
            "продан", "снят с продажи")
TRANSITIONS = {
    "в пути": {"на складе", "снят с продажи"},
    "на складе": {"в резерве", "на тест-драйве", "продан", "снят с продажи"},
    "в резерве": {"на складе", "продан"},
    "на тест-драйве": {"на складе", "в резерве"},
    "продан": set(),
    "снят с продажи": {"на складе"},
}


class AccountLocked(Exception):
    pass


def validate_vin(vin):
    if not isinstance(vin, str):
        return False
    return bool(VIN_RE.match(vin.strip().upper()))


def change_status(current, new):
    if new not in TRANSITIONS.get(current, set()):
        raise ValueError(f"{current} -> {new}")
    return new


class AuthService:
    def __init__(self, users):
        self._users = dict(users)
        self._fails = {}
        self._locked = set()

    def login(self, user, password):
        if user in self._locked:
            raise AccountLocked(user)
        if self._users.get(user) == password:
            self._fails[user] = 0
            return True
        self._fails[user] = self._fails.get(user, 0) + 1
        if self._fails[user] >= MAX_ATTEMPTS:
            self._locked.add(user)
        return False

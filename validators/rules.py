import re
from datetime import date, datetime
from typing import Any

from .base import Rule, ConfigError

_NOT_SET = object()  # маркер «привести не удалось»

_DATE_FORMATS = (
    "%Y-%m-%d",   
    "%d-%m-%Y",   
    "%d.%m.%Y",   
    "%Y.%m.%d",   
)


def _is_missing(value: Any) -> bool:
    return value is None


def _parse_date(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        s = value.strip()
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(s, fmt).date()
            except ValueError:
                continue
    return None


def _looks_like_date(value: Any) -> bool:
    return isinstance(value, (date, datetime)) or (
        isinstance(value, str) and _parse_date(value) is not None
    )


def _to_int(value: Any) -> Any:
    #Привести к int или вернуть _NOT_SET.
    if isinstance(value, bool):
        return _NOT_SET
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else _NOT_SET
    if isinstance(value, str):
        s = value.strip()
        try:
            return int(s)
        except ValueError:
            return _NOT_SET
    return _NOT_SET


def _to_float(value: Any) -> Any:
    # Привести к float или вернуть _NOT_SET.
    if isinstance(value, bool):
        return _NOT_SET
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        s = value.strip()
        try:
            return float(s)
        except ValueError:
            return _NOT_SET
    return _NOT_SET


def _to_bool(value: Any) -> Any:
    # Привести к bool или вернуть _NOT_SET.
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        s = value.strip().lower()
        if s in ("true", "1", "yes", "y"):
            return True
        if s in ("false", "0", "no", "n"):
            return False
    return _NOT_SET

class RequiredRule(Rule):
    # Значение не должно быть None.
    rule_type = "required"

    def __init__(self, field_name: str, required: bool = True) -> None:
        super().__init__(field_name)
        self.required = bool(required)

    def validate(self, value: Any) -> list[str]:
        if self.required and _is_missing(value):
            return [f"поле '{self.field_name}' обязательно"]
        return []


class TypeRule(Rule):
    # Проверка типа
    rule_type = "type"

    _ALLOWED = {"integer", "float", "string", "date", "boolean"}

    def __init__(self, field_name: str, type: str) -> None:
        super().__init__(field_name)
        if type not in self._ALLOWED:
            raise ConfigError(
                f"Поле '{field_name}': неизвестный тип '{type}'. "
                f"Доступно: {', '.join(sorted(self._ALLOWED))}"
            )
        self.expected = type

    def validate(self, value: Any) -> list[str]:
        if _is_missing(value):
            return []  # отсутствие проверяет required
        if self._coerce(value) is not _NOT_SET:
            return []
        return [f"поле '{self.field_name}' должно быть {self.expected}"]

    def _coerce(self, value: Any) -> Any:
        """Вернуть приведённое значение или _NOT_SET, если привести нельзя."""
        t = self.expected
        if t == "string":
            return value if isinstance(value, str) else _NOT_SET
        if t == "integer":
            return _to_int(value)
        if t == "float":
            return _to_float(value)
        if t == "boolean":
            return _to_bool(value)
        if t == "date":
            d = _parse_date(value)
            return d if d is not None else _NOT_SET
        return _NOT_SET


class RangeRule(Rule):
    #Диапазон min/max для чисел и дат.
    rule_type = "range"

    def __init__(
        self,
        field_name: str,
        min: Any | None = None,
        max: Any | None = None,
    ) -> None:
        super().__init__(field_name)
        if min is None and max is None:
            raise ConfigError(
                f"Поле '{field_name}': правило 'range' требует min и/или max"
            )
        self.min = min
        self.max = max

    def validate(self, value: Any) -> list[str]:
        if _is_missing(value):
            return []
        if (
            _parse_date(value) is not None
            or _looks_like_date(self.min)
            or _looks_like_date(self.max)
        ):
            return self._validate_date(value)

        return self._validate_number(value)

    def _validate_number(self, value: Any) -> list[str]:
        num = _to_float(value)
        if num is _NOT_SET:
            return [
                f"поле '{self.field_name}' должно быть числом для проверки диапазона"
            ]
        errors = []
        if self.min is not None and num < self.min:
            errors.append(f"поле '{self.field_name}' меньше минимума ({self.min})")
        if self.max is not None and num > self.max:
            errors.append(f"поле '{self.field_name}' больше максимума ({self.max})")
        return errors

    def _validate_date(self, value: Any) -> list[str]:
        d = _parse_date(value)
        if d is None:
            return [
                f"поле '{self.field_name}' не является датой для проверки диапазона"
            ]
        lo = _parse_date(self.min) if self.min is not None else None
        hi = _parse_date(self.max) if self.max is not None else None
        errors = []
        if lo is not None and d < lo:
            errors.append(f"поле '{self.field_name}' раньше минимума ({self.min})")
        if hi is not None and d > hi:
            errors.append(f"поле '{self.field_name}' позже максимума ({self.max})")
        return errors


class PatternRule(Rule):
    #Регулярное выражение
    rule_type = "pattern"

    def __init__(self, field_name: str, pattern: str) -> None:
        super().__init__(field_name)
        try:
            self._re = re.compile(pattern)
        except re.error as e:
            raise ConfigError(
                f"Поле '{field_name}': некорректный pattern '{pattern}': {e}"
            )

    def validate(self, value: Any) -> list[str]:
        if _is_missing(value):
            return []
        if not isinstance(value, str):
            return [
                f"поле '{self.field_name}' должно быть строкой для проверки pattern"
            ]
        if self._re.fullmatch(value) is None:
            return [f"поле '{self.field_name}' не соответствует формату"]
        return []


class UniqueRule(Rule):
    # Уникальность значения в пределах всего набора
    rule_type = "unique"

    def __init__(self, field_name: str, unique: bool = True) -> None:
        super().__init__(field_name)
        self.unique = bool(unique)

    def validate(self, value: Any) -> list[str]:
        return []  


class LengthRule(Rule):
    #Длина строки: min_length/max_length.
    rule_type = "length"

    def __init__(
        self,
        field_name: str,
        min_length: int | None = None,
        max_length: int | None = None,
    ) -> None:
        super().__init__(field_name)
        if min_length is None and max_length is None:
            raise ConfigError(
                f"Поле '{field_name}': правило 'length' требует min_length и/или max_length"
            )
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> list[str]:
        if _is_missing(value):
            return []
        if not isinstance(value, str):
            return [
                f"поле '{self.field_name}' должно быть строкой для проверки длины"
            ]
        errors = []
        if self.min_length is not None and len(value) < self.min_length:
            errors.append(
                f"поле '{self.field_name}' короче минимума ({self.min_length})"
            )
        if self.max_length is not None and len(value) > self.max_length:
            errors.append(
                f"поле '{self.field_name}' длиннее максимума ({self.max_length})"
            )
        return errors
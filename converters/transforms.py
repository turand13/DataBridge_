"""Трансформации значений"""
from datetime import datetime, timezone
from typing import Any

from .base import Transform, TransformError


class _StrOnly(Transform):
    """База для трансформаций, работающих только со строками

    None и не-str проходят без изменений
    """

    def _apply(self, s: str) -> str:
        raise NotImplementedError

    def __call__(self, value: Any) -> Any:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        return self._apply(value)


class UpperCase(_StrOnly):
    """Привести строку к верхнему регистру"""

    def _apply(self, s: str) -> str:
        return s.upper()


class LowerCase(_StrOnly):
    """Привести строку к нижнему регистру"""

    def _apply(self, s: str) -> str:
        return s.lower()


class Trim(_StrOnly):
    """Обрезать пробелы по краям"""

    def _apply(self, s: str) -> str:
        return s.strip()


class DictReplace(Transform):
    """Заменить значение по словарю

    Словарь {исходное: новое}. Если значения нет в словаре, то вернуть как есть
    Применяется к любому типу (ключи словаря могут быть не только str)
    """

    def __init__(self, table: dict[Any, Any]) -> None:
        if not isinstance(table, dict):
            raise TransformError("DictReplace: table должен быть словарём")
        self.table = table

    def __call__(self, value: Any) -> Any:
        if value is None:
            return None
        return self.table.get(value, value)


class TimestampToDate(Transform):
    """Преобразовать UNIX timestamp в строку даты 'DD-MM-YYYY'

    Принимает int/float или строку с числом.
    Если не timestamp — вернуть без изменений
    """

    def __init__(self, tz: timezone | None = None) -> None:
        self.tz = tz or timezone.utc

    def __call__(self, value: Any) -> Any:
        if value is None:
            return None
        ts = self._as_number(value)
        if ts is None:
            return value
        try:
            dt = datetime.fromtimestamp(ts, tz=self.tz)
        except (OverflowError, OSError, ValueError):
            return value
        return dt.strftime("%d.%m.%Y")

    @staticmethod
    def _as_number(value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            s = value.strip()
            try:
                return float(s)
            except ValueError:
                return None
        return None
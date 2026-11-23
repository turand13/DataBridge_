"""Переименование полей по словарю mapping"""
from typing import Any

from .base import ConfigError


class FieldMapper:
    """Переименовывает ключи в записях по словарю {старое: новое}."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        mapping = mapping or {}
        if not isinstance(mapping, dict):
            raise ConfigError("mapping должен быть словарём {старое: новое}")
        for old, new in mapping.items():
            if not isinstance(old, str) or not isinstance(new, str):
                raise ConfigError(
                    f"mapping: ключи и значения должны быть строками, "
                    f"получено {old!r}: {new!r}"
                )
        self.mapping = dict(mapping)

    def apply(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Вернуть новые записи с переименованными ключами"""
        if not self.mapping:
            return [dict(r) for r in rows]
        result: list[dict[str, Any]] = []
        for row in rows:
            new_row: dict[str, Any] = {}
            for key, value in row.items():
                new_key = self.mapping.get(key, key)
                if new_key in new_row:
                    raise ConfigError(
                        f"mapping: после переименования ключ '{new_key}' дублируется "
                        f"(из '{key}')"
                    )
                new_row[new_key] = value
            result.append(new_row)
        return result
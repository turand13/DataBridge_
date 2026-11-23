"""Команда stats. Статистика по файлу без схемы валидации"""
from pathlib import Path
from typing import Any

from readers.registry import read_file


def run(input_path: Path) -> int:
    """Вывести статистику по файлу. Возвращает exit code."""
    rows = read_file(input_path)

    columns = _collect_columns(rows)
    print(f"Файл: {input_path}")
    print(f"Записей: {len(rows)}")
    print(f"Колонок: {len(columns)}")

    if not rows:
        return 0

    print()
    print(f"{'Колонка':<20} {'Заполнено':>10} {'Пусто':>8} {'Уникальных':>12}")
    print("-" * 54)
    for col in columns:
        filled = 0
        unique: set[Any] = set()
        for row in rows:
            value = row.get(col)
            if value is None or value == "":
                continue
            filled += 1
            unique.add(_hashable(value))
        empty = len(rows) - filled
        print(f"{col:<20} {filled:>10} {empty:>8} {len(unique):>12}")
    return 0


def _collect_columns(rows: list[dict[str, Any]]) -> list[str]:
    """Объединение ключей всех записей в порядке первого появления."""
    seen: dict[str, None] = {}
    for row in rows:
        for k in row:
            seen.setdefault(k, None)
    return list(seen)


def _hashable(value: Any) -> Any:
    """Привести значение к хешируемому виду"""
    try:
        hash(value)
        return value
    except TypeError:
        return repr(value)
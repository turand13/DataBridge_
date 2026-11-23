"""Запись CSV-файлов"""
import csv
from pathlib import Path
from typing import Any

from ._normalize import to_text
from .base import Writer, DataWriteError


class CsvWriter(Writer):
    """Writer для CSV: заголовки из ключей, значения через to_text"""

    extensions = (".csv",)

    def __init__(self, delimiter: str = ",") -> None:
        self.delimiter = delimiter

    def write(self, rows: list[dict[str, Any]], path: Path) -> None:
        if not rows:
            try:
                path.write_text("", encoding="utf-8")
            except OSError as e:
                raise DataWriteError(f"Не удалось записать {path.name}: {e}")
            return

        headers = self._collect_headers(rows)
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=headers, delimiter=self.delimiter)
                writer.writeheader()
                for row in rows:
                    writer.writerow({k: to_text(row.get(k)) for k in headers})
        except OSError as e:
            raise DataWriteError(f"Не удалось записать {path.name}: {e}")

    @staticmethod
    def _collect_headers(rows: list[dict[str, Any]]) -> list[str]:
        """Объединение ключей всех записей в порядке первого появления"""
        seen: dict[str, None] = {}
        for row in rows:
            for k in row:
                seen.setdefault(k, None)
        return list(seen)
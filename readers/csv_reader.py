"""Чтение CSV-файлов"""
import csv
from pathlib import Path
from typing import Any

from .base import Reader, DataReadError


class CsvReader(Reader):
    """Reader для CSV с заголовками или без, настраиваемым разделителем"""

    extensions = (".csv",)

    def __init__(self, delimiter: str = ",", has_header: bool = True) -> None:
        self.delimiter = delimiter
        self.has_header = has_header

    def read(self, path: Path) -> list[dict[str, Any]]:
        try:
            with open(path, encoding="utf-8-sig", newline="") as f:
                if self.has_header:
                    reader = csv.DictReader(f, delimiter=self.delimiter)
                    return [self._clean(row) for row in reader]
                return self._read_without_header(f)
        except UnicodeDecodeError:
            raise DataReadError(
                f"Файл {path.name} не в UTF-8. Проверьте кодировку."
            )
        except csv.Error as e:
            raise DataReadError(f"Сломаный CSV {path.name}: {e}")

    def _read_without_header(self, f) -> list[dict[str, Any]]:
        reader = csv.reader(f, delimiter=self.delimiter)
        rows = list(reader)
        if not rows:
            return []
        n = len(rows[0])
        header = [f"col{i + 1}" for i in range(n)]
        return [
            {header[i]: (val if val != "" else None) for i, val in enumerate(r)}
            for r in rows
        ]

    @staticmethod
    def _clean(row: dict) -> dict:
        return {k: (v if v != "" else None) for k, v in row.items()}
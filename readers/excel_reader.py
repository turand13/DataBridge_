"""Чтение Excel-файлов (.xlsx)"""
import zipfile
from pathlib import Path
from typing import Any

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from .base import Reader, DataReadError


class ExcelReader(Reader):
    """Reader для .xlsx: первый (или указанный) лист, первая строка — заголовки"""

    extensions = (".xlsx",)

    def __init__(self, sheet_name: str | None = None) -> None:
        self.sheet_name = sheet_name

    def read(self, path: Path) -> list[dict[str, Any]]:
        try:
            wb = load_workbook(path, read_only=True, data_only=True)
        except (InvalidFileException, KeyError, zipfile.BadZipFile, OSError) as e:
            raise DataReadError(f"Не удалось открыть Excel {path.name}: {e}")

        try:
            if self.sheet_name is not None:
                if self.sheet_name not in wb.sheetnames:
                    raise DataReadError(
                        f"Excel {path.name}: лист '{self.sheet_name}' не найден. "
                        f"Доступно: {', '.join(wb.sheetnames)}"
                    )
                ws = wb[self.sheet_name]
            else:
                ws = wb.worksheets[0]

            rows_iter = ws.iter_rows(values_only=True)
            try:
                header_row = next(rows_iter)
            except StopIteration:
                return []

            headers = [str(h) if h is not None else f"col{i + 1}" for i, h in enumerate(header_row)]

            result: list[dict[str, Any]] = []
            for row in rows_iter:
                if all(v is None for v in row):
                    continue
                record = {
                    headers[i]: (row[i] if i < len(row) else None)
                    for i in range(len(headers))
                }
                result.append(record)
            return result
        finally:
            wb.close()
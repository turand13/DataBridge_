"""Запись Excel-файлов (.xlsx)"""
from datetime import date, datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook

from .base import Writer, DataWriteError


class ExcelWriter(Writer):
    """Writer для .xlsx"""

    extensions = (".xlsx",)

    def __init__(self, sheet_name: str = "Sheet1") -> None:
        self.sheet_name = sheet_name

    def write(self, rows: list[dict[str, Any]], path: Path) -> None:
        wb = Workbook()
        ws = wb.active
        ws.title = self.sheet_name

        headers = self._collect_headers(rows)
        if headers:
            ws.append(headers)
            for row in rows:
                values = [row.get(h) for h in headers]
                ws.append(values)
                # Формат отображения дат в Excel: dd.mm.yyyy
                for cell, value in zip(ws[ws.max_row], values):
                    if isinstance(value, datetime):
                        cell.number_format = "DD.MM.YYYY HH:MM:SS"
                    elif isinstance(value, date):
                        cell.number_format = "DD.MM.YYYY"

        try:
            wb.save(path)
        except OSError as e:
            raise DataWriteError(f"Не удалось записать {path.name}: {e}")
        finally:
            wb.close()

    @staticmethod
    def _collect_headers(rows: list[dict[str, Any]]) -> list[str]:
        seen: dict[str, None] = {}
        for row in rows:
            for k in row:
                seen.setdefault(k, None)
        return list(seen)
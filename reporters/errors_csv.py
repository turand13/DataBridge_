#Сохранение некорректных записей в errors.csv

from pathlib import Path

from validators import ValidationResult
from writers.base import DataWriteError
from writers.csv_writer import CsvWriter

_ROW_INDEX = "row_index"
_ERRORS = "errors"


def write_errors_csv(result: ValidationResult, path: Path) -> None:
    #Записать невалидные записи и причины в errors.csv

    rows = _build_rows(result)
    if not rows:
        # Пустой результат: создаём файл с фиксированным заголовком.
        try:
            path.write_text(f"{_ROW_INDEX},{_ERRORS}\n", encoding="utf-8")
        except OSError as e:
            raise DataWriteError(f"Не удалось записать {path.name}: {e}")
        return
    CsvWriter().write(rows, path)


def _build_rows(result: ValidationResult) -> list[dict]:
    #Собрать строки для errors.csv из ValidationResult.
    issues_by_row: dict[int, list[str]] = {}
    for issue in result.issues:
        issues_by_row.setdefault(issue.row_index, []).append(
            f"{issue.field}: {issue.message}"
        )

    headers = _collect_headers(result.invalid_rows)

    rows: list[dict] = []
    for row, row_index in zip(result.invalid_rows, result.invalid_row_indices):
        errors = "; ".join(issues_by_row.get(row_index, []))
        entry: dict = {_ROW_INDEX: row_index}
        for h in headers:
            entry[h] = row.get(h)
        entry[_ERRORS] = errors
        rows.append(entry)
    return rows


def _collect_headers(rows: list[dict]) -> list[str]:
    #Объединение ключей всех записей в порядке первого появления
    seen: dict[str, None] = {}
    for row in rows:
        for k in row:
            seen.setdefault(k, None)
    return list(seen)
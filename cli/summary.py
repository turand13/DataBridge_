"""Печать сводки о результате обработки в консоль"""
from pathlib import Path

from validators import ValidationResult


MAX_ISSUES_TO_PRINT = 10


def print_summary(
    result: ValidationResult,
    output_path: Path | None = None,
    errors_path: Path | None = None,
    report_path: Path | None = None,
) -> None:
    """Напечатать сводку: всего / успешно / ошибок / первые N ошибок / пути файлов."""
    print(f"Всего записей: {result.total}")
    print(f"Успешно обработано: {len(result.valid_rows)}")
    print(f"Ошибок: {result.errors_count}")

    for issue in result.issues[:MAX_ISSUES_TO_PRINT]:
        print(f"  Запись {issue.row_index}: поле \"{issue.field}\" — {issue.message}")
    if result.errors_count > MAX_ISSUES_TO_PRINT:
        print(f"  ... и ещё {result.errors_count - MAX_ISSUES_TO_PRINT}")

    if output_path is not None:
        print(f"Результат сохранён: {output_path}")
    if errors_path is not None:
        print(f"Ошибки сохранены: {errors_path}")
    if report_path is not None:
        print(f"Отчёт сохранён: {report_path}")
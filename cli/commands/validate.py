"""Команда validate"""
from pathlib import Path

from readers.registry import read_file
from reporters import write_errors_csv, write_html_report
from validators import load_schema, validate

from cli.summary import print_summary


def run(
    input_path: Path,
    config_path: Path,
    report_path: Path | None = None,
    errors_path: Path | None = None,
) -> int:
    """Выполнить validate. Возвращает exit code."""
    rows = read_file(input_path)
    schema = load_schema(config_path)
    result = validate(rows, schema)

    if errors_path is not None:
        write_errors_csv(result, errors_path)
    if report_path is not None:
        write_html_report(result, report_path)

    print_summary(
        result,
        output_path=None,
        errors_path=errors_path,
        report_path=report_path,
    )
    return 0
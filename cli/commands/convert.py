"""Команда convert"""
from pathlib import Path

from converters import load_convert_config
from readers.registry import read_file
from reporters import write_errors_csv, write_html_report
from validators import load_schema, validate
from writers.registry import get_writer

from cli.summary import print_summary


def run(
    input_path: Path,
    to_format: str,
    config_path: Path,
    output_path: Path,
    report_path: Path | None = None,
    errors_path: Path | None = None,
) -> int:
    """Выполнить convert. Возвращает exit code.

    Ошибки данных пробрасываются наружу — их ловит cli.errors.handle_errors.
    """
    rows = read_file(input_path)
    schema = load_schema(config_path)
    result = validate(rows, schema)

    transformer = load_convert_config(config_path)
    converted = transformer.apply(result.valid_rows)

    writer = get_writer(to_format)
    writer.write(converted, output_path)

    wrote_errors = False
    if errors_path is not None:
        write_errors_csv(result, errors_path)
        wrote_errors = True

    # HTML-отчёт — по запросу.
    if report_path is not None:
        write_html_report(result, report_path)

    print_summary(
        result,
        output_path=output_path,
        errors_path=errors_path if wrote_errors else None,
        report_path=report_path,
    )
    return 0
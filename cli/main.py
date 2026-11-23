"""Точка входа CLI DataBridge: сборка argparse и диспетчеризация команд"""
import argparse
import sys
from pathlib import Path

from cli.commands import convert as convert_cmd
from cli.commands import stats as stats_cmd
from cli.commands import validate as validate_cmd
from cli.errors import run_with_errors


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="databridge",
        description="DataBridge — чтение, валидация и конвертация данных "
                    "(CSV, JSON, XML, Excel).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # convert
    p_convert = sub.add_parser("convert", help="Прочитать файл, провалидировать, "
                                               "сконвертировать и записать в другой формат")
    p_convert.add_argument("input", type=Path, help="Входной файл (csv/json/xml/xlsx)")
    p_convert.add_argument("--to", required=True, dest="to_format",
                           choices=["csv", "json", "xml", "xlsx", "excel"],
                           help="Целевой формат")
    p_convert.add_argument("--config", required=True, type=Path,
                           help="YAML-конфиг (валидация + mapping/transforms)")
    p_convert.add_argument("--output", required=True, type=Path,
                           help="Куда сохранить результат")
    p_convert.add_argument("--report", type=Path, default=None,
                           help="Куда сохранить HTML-отчёт (необязательно)")
    p_convert.add_argument("--errors", type=Path, default=None,
                           help="Куда сохранить errors.csv (необязательно)")

    # validate
    p_validate = sub.add_parser("validate", help="Прочитать файл и провалидировать по схеме")
    p_validate.add_argument("input", type=Path)
    p_validate.add_argument("--config", required=True, type=Path)
    p_validate.add_argument("--report", type=Path, default=None)
    p_validate.add_argument("--errors", type=Path, default=None)

    # stats
    p_stats = sub.add_parser("stats", help="Показать статистику по файлу (без схемы)")
    p_stats.add_argument("input", type=Path)

    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа. Возвращает exit code"""
    parser = build_parser()
    args = parser.parse_args(argv)

    def _dispatch() -> int:
        if args.command == "convert":
            return convert_cmd.run(
                input_path=args.input,
                to_format=args.to_format,
                config_path=args.config,
                output_path=args.output,
                report_path=args.report,
                errors_path=args.errors,
            )
        if args.command == "validate":
            return validate_cmd.run(
                input_path=args.input,
                config_path=args.config,
                report_path=args.report,
                errors_path=args.errors,
            )
        if args.command == "stats":
            return stats_cmd.run(input_path=args.input)

        parser.print_help()
        return 2

    return run_with_errors(_dispatch)


if __name__ == "__main__":
    sys.exit(main())
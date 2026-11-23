"""Единая обработка ошибок CLI: превращает исключения в понятные сообщения"""
import sys
from typing import Callable

from readers.base import DataReadError
from writers.base import DataWriteError
from validators import ConfigError as ValidatorConfigError
from converters import ConfigError as ConverterConfigError


EXIT_OK = 0
EXIT_DATA_ERROR = 1
EXIT_INTERNAL = 3


_KNOWN_ERRORS = (
    DataReadError,
    DataWriteError,
    ValidatorConfigError,
    ConverterConfigError,
)


def run_with_errors(fn: Callable[[], int]) -> int:
    """Выполнить fn, поймать известные ошибки и вернуть exit-code.
    main() остаётся чистой функцией: возвращает int, не делает sys.exit.
    """
    try:
        return fn()
    except _KNOWN_ERRORS as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        return EXIT_DATA_ERROR
    except KeyboardInterrupt:
        print("Прервано пользователем", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Внутренняя ошибка: {e}", file=sys.stderr)
        return EXIT_INTERNAL
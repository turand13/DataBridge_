"""Фабрика Reader'ов: выбор по расширению файла"""
from pathlib import Path
from .base import Reader, DataReadError
from .csv_reader import CsvReader
from .json_reader import JsonReader
from .xml_reader import XmlReader
from .excel_reader import ExcelReader

# Реестр всех зарегистрированных Reader'ов.
# Добавление нового формата = добавить экземпляр в этот список.
_READERS: list[Reader] = [
    CsvReader(),
    JsonReader(),
    XmlReader(),
    ExcelReader(),
]


def get_reader(path: Path) -> Reader:
    """Подобрать Reader по расширению файла"""
    ext = path.suffix.lower()
    for reader in _READERS:
        if ext in reader.extensions:
            return reader
    available = ", ".join(e for r in _READERS for e in r.extensions)
    raise DataReadError(
        f"Неподдерживаемый формат '{ext}'. Доступно: {available}"
    )


def read_file(path: Path) -> list[dict]:
    """Прочитать файл, определив формат по расширению"""
    if not path.exists():
        raise DataReadError(f"Файл не найден: {path}")
    return get_reader(path).read(path)
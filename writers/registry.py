"""Фабрика Writer'ов, выбор по имени формата"""
from .base import Writer, DataWriteError
from .csv_writer import CsvWriter
from .json_writer import JsonWriter
from .xml_writer import XmlWriter
from .excel_writer import ExcelWriter

_WRITERS: dict[str, Writer] = {
    "csv": CsvWriter(),
    "json": JsonWriter(),
    "xml": XmlWriter(),
    "xlsx": ExcelWriter(),
    "excel": ExcelWriter(), 
}


def get_writer(format_name: str) -> Writer:
    """Подобрать Writer по имени формата ('csv', 'json', 'xml', 'xlsx')."""
    key = format_name.lower().lstrip(".")
    if key not in _WRITERS:
        raise DataWriteError(
            f"Неподдерживаемый формат записи '{format_name}'. "
            f"Доступно: csv, json, xml, xlsx"
        )
    return _WRITERS[key]
"""Unit-тесты для Writer'ов"""
from datetime import date, datetime
from pathlib import Path

import pytest

from writers.base import DataWriteError
from writers.csv_writer import CsvWriter
from writers.excel_writer import ExcelWriter
from writers.json_writer import JsonWriter
from writers.registry import get_writer
from writers.xml_writer import XmlWriter

from readers.csv_reader import CsvReader
from readers.json_reader import JsonReader
from readers.xml_reader import XmlReader
from readers.excel_reader import ExcelReader


ROWS = [
    {"id": 1, "name": "Иван", "email": "ivan@mail.ru"},
    {"id": 2, "name": "Мария", "email": "maria@mail.ru"},
]


#CSV Writer

def test_csv_write_basic(tmp_path: Path) -> None:
    p = tmp_path / "out.csv"
    CsvWriter().write(ROWS, p)
    text = p.read_text(encoding="utf-8")
    assert "id,name,email" in text.splitlines()[0]


def test_csv_write_none_as_empty(tmp_path: Path) -> None:
    p = tmp_path / "out.csv"
    CsvWriter().write([{"id": 1, "name": None}], p)
    lines = p.read_text(encoding="utf-8").splitlines()
    assert lines[1] == "1,"


def test_csv_write_empty_rows_creates_empty_file(tmp_path: Path) -> None:
    p = tmp_path / "out.csv"
    CsvWriter().write([], p)
    assert p.read_text(encoding="utf-8") == ""


def test_csv_write_unions_keys(tmp_path: Path) -> None:
    p = tmp_path / "out.csv"
    CsvWriter().write([{"a": 1}, {"b": 2}], p)
    header = p.read_text(encoding="utf-8").splitlines()[0]
    assert header == "a,b"


def test_csv_write_to_unwritable_path_raises(tmp_path: Path) -> None:
    p = tmp_path / "no_such_dir" / "out.csv"
    with pytest.raises(DataWriteError):
        CsvWriter().write(ROWS, p)


#JSON Writer

def test_json_write_basic(tmp_path: Path) -> None:
    p = tmp_path / "out.json"
    JsonWriter().write(ROWS, p)
    text = p.read_text(encoding="utf-8")
    assert "Иван" in text  # ensure_ascii=False
    assert text.strip().startswith("[")


def test_json_write_datetime_becomes_iso(tmp_path: Path) -> None:
    p = tmp_path / "out.json"
    JsonWriter().write([{"id": 1, "d": datetime(2024, 5, 1, 12, 0)}], p)
    assert '"2024-05-01T12:00:00"' in p.read_text(encoding="utf-8")


def test_json_write_date_becomes_iso(tmp_path: Path) -> None:
    p = tmp_path / "out.json"
    JsonWriter().write([{"d": date(2024, 5, 1)}], p)
    assert '"01.05.2024"' in p.read_text(encoding="utf-8")


def test_json_write_empty(tmp_path: Path) -> None:
    p = tmp_path / "out.json"
    JsonWriter().write([], p)
    assert p.read_text(encoding="utf-8").strip() == "[]"


#XML Writer

def test_xml_write_basic(tmp_path: Path) -> None:
    p = tmp_path / "out.xml"
    XmlWriter().write(ROWS, p)
    text = p.read_text(encoding="utf-8")
    assert "<records>" in text
    assert "<record>" in text
    assert "<name>Иван</name>" in text


def test_xml_write_none_as_empty_tag(tmp_path: Path) -> None:
    p = tmp_path / "out.xml"
    XmlWriter().write([{"id": 1, "name": None}], p)
    # пустое значение -> тег без текста
    assert "<name />" in p.read_text(encoding="utf-8") or "<name/>" in p.read_text(encoding="utf-8")


def test_xml_write_empty(tmp_path: Path) -> None:
    p = tmp_path / "out.xml"
    XmlWriter().write([], p)
    text = p.read_text(encoding="utf-8")
    assert "<records" in text


#Excel Writer

def test_excel_write_basic(tmp_path: Path) -> None:
    p = tmp_path / "out.xlsx"
    ExcelWriter().write(ROWS, p)
    assert p.exists() and p.stat().st_size > 0


def test_excel_write_datetime_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "out.xlsx"
    ExcelWriter().write([{"id": 1, "d": datetime(2024, 5, 1, 12, 0)}], p)
    rows = ExcelReader().read(p)
    # openpyxl вернёт datetime из ячейки
    assert isinstance(rows[0]["d"], datetime)


def test_excel_write_empty(tmp_path: Path) -> None:
    p = tmp_path / "out.xlsx"
    ExcelWriter().write([], p)
    assert p.exists()


#Реестр

def test_get_writer_csv() -> None:
    assert isinstance(get_writer("csv"), CsvWriter)


def test_get_writer_json() -> None:
    assert isinstance(get_writer("json"), JsonWriter)


def test_get_writer_excel_alias() -> None:
    assert isinstance(get_writer("excel"), ExcelWriter)


def test_get_writer_unknown_raises() -> None:
    with pytest.raises(DataWriteError):
        get_writer("yaml")


def test_get_writer_strips_dot() -> None:
    assert isinstance(get_writer(".json"), JsonWriter)


#  Round-trip: write -> read -> equals 

def test_roundtrip_csv(tmp_path: Path) -> None:
    p = tmp_path / "rt.csv"
    CsvWriter().write(ROWS, p)
    got = CsvReader().read(p)
    # CSV возвращает строки
    assert got == [
        {"id": "1", "name": "Иван", "email": "ivan@mail.ru"},
        {"id": "2", "name": "Мария", "email": "maria@mail.ru"},
    ]


def test_roundtrip_json(tmp_path: Path) -> None:
    p = tmp_path / "rt.json"
    JsonWriter().write(ROWS, p)
    assert JsonReader().read(p) == ROWS


def test_roundtrip_xml(tmp_path: Path) -> None:
    p = tmp_path / "rt.xml"
    XmlWriter().write(ROWS, p)
    # XML возвращает строки
    assert XmlReader().read(p) == [
        {"id": "1", "name": "Иван", "email": "ivan@mail.ru"},
        {"id": "2", "name": "Мария", "email": "maria@mail.ru"},
    ]


def test_roundtrip_excel(tmp_path: Path) -> None:
    p = tmp_path / "rt.xlsx"
    ExcelWriter().write(ROWS, p)
    got = ExcelReader().read(p)
    assert got == ROWS  

def test_csv_write_date_is_dd_mm_yyyy(tmp_path: Path) -> None:
    p = tmp_path / "out.csv"
    CsvWriter().write([{"d": date(2024, 5, 1)}], p)
    assert "01.05.2024" in p.read_text(encoding="utf-8")


def test_to_text_datetime_is_iso() -> None:
    from writers._normalize import to_text
    assert to_text(datetime(2024, 5, 1, 12, 0)) == "2024-05-01T12:00:00"


def test_to_text_date_is_dd_mm_yyyy() -> None:
    from writers._normalize import to_text
    assert to_text(date(2024, 5, 1)) == "01.05.2024"
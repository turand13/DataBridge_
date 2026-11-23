"""Unit-тесты для Reader'ов и реестра форматов."""
from pathlib import Path
import pytest

from readers.base import DataReadError
from readers.csv_reader import CsvReader
from readers.json_reader import JsonReader
from readers.xml_reader import XmlReader
from readers.registry import get_reader, read_file
from openpyxl import Workbook
from readers.excel_reader import ExcelReader

# ---------- CSV с заголовком ----------

def test_csv_with_header(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("id,name\n1,Иван\n2,Мария\n", encoding="utf-8")
    rows = CsvReader().read(p)
    assert rows == [
        {"id": "1", "name": "Иван"},
        {"id": "2", "name": "Мария"},
    ]


def test_csv_empty_field_becomes_none(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("id,name\n1,\n", encoding="utf-8")
    rows = CsvReader().read(p)
    assert rows[0]["name"] is None


def test_csv_bom_is_stripped(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("\ufeffid,name\n1,Иван\n", encoding="utf-8")
    rows = CsvReader().read(p)
    assert list(rows[0].keys()) == ["id", "name"]


def test_csv_empty_file_returns_empty_list(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("", encoding="utf-8")
    assert CsvReader().read(p) == []


def test_csv_only_header_returns_empty_list(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("id,name\n", encoding="utf-8")
    assert CsvReader().read(p) == []


# ---------- CSV без заголовка ----------

def test_csv_without_header(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("1,Иван\n2,Мария\n", encoding="utf-8")
    rows = CsvReader(has_header=False).read(p)
    assert rows[0] == {"col1": "1", "col2": "Иван"}


# ---------- Настраиваемый разделитель ----------

def test_csv_custom_delimiter(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("id;name\n1;Иван\n", encoding="utf-8")
    rows = CsvReader(delimiter=";").read(p)
    assert rows == [{"id": "1", "name": "Иван"}]


# ---------- Ошибки чтения ----------

def test_csv_broken_unicode_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_bytes(b"\xff\xfe\x00id\n")  # невалидный UTF-8
    with pytest.raises(DataReadError):
        CsvReader().read(p)


# ---------- Реестр ----------

def test_registry_returns_csv_reader(tmp_path: Path) -> None:
    p = tmp_path / "a.csv"
    p.write_text("id\n1\n", encoding="utf-8")
    assert isinstance(get_reader(p), CsvReader)


def test_registry_unknown_extension_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.txt"
    p.write_text("x", encoding="utf-8")
    with pytest.raises(DataReadError):
        get_reader(p)


def test_read_file_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(DataReadError):
        read_file(tmp_path / "nope.csv")


def test_read_file_on_sample(tmp_path: Path) -> None:
    sample = Path("samples/valid.csv")
    rows = read_file(sample)
    assert len(rows) == 3
    assert rows[0]["name"] == "Иван"

    # ---------- JSON ----------

def test_json_array_of_objects(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text('[{"id": 1, "name": "Иван"}]', encoding="utf-8")
    rows = JsonReader().read(p)
    assert rows == [{"id": 1, "name": "Иван"}]


def test_json_empty_array(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text("[]", encoding="utf-8")
    assert JsonReader().read(p) == []


def test_json_broken_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text('{"id": 1', encoding="utf-8")
    with pytest.raises(DataReadError):
        JsonReader().read(p)


def test_json_root_not_array_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text('{"id": 1}', encoding="utf-8")
    with pytest.raises(DataReadError):
        JsonReader().read(p)


def test_json_array_of_non_objects_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text('[1, 2, 3]', encoding="utf-8")
    with pytest.raises(DataReadError):
        JsonReader().read(p)


def test_json_null_becomes_none(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text('[{"id": 1, "name": null}]', encoding="utf-8")
    assert JsonReader().read(p)[0]["name"] is None


def test_registry_returns_json_reader(tmp_path: Path) -> None:
    p = tmp_path / "a.json"
    p.write_text("[]", encoding="utf-8")
    assert isinstance(get_reader(p), JsonReader)

# ---------- XML ----------

def test_xml_flat_structure(tmp_path: Path) -> None:
    p = tmp_path / "a.xml"
    p.write_text(
        "<records>"
        "<record><id>1</id><name>Иван</name></record>"
        "<record><id>2</id><name>Мария</name></record>"
        "</records>",
        encoding="utf-8",
    )
    rows = XmlReader().read(p)
    assert rows == [
        {"id": "1", "name": "Иван"},
        {"id": "2", "name": "Мария"},
    ]


def test_xml_empty_tag_becomes_none(tmp_path: Path) -> None:
    p = tmp_path / "a.xml"
    p.write_text("<records><record><id>1</id><name/></record></records>", encoding="utf-8")
    assert XmlReader().read(p)[0]["name"] is None


def test_xml_broken_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.xml"
    p.write_text("<records><record>", encoding="utf-8")
    with pytest.raises(DataReadError):
        XmlReader().read(p)


def test_xml_nested_field_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.xml"
    p.write_text(
        "<records><record><id>1</id><address><city>M</city></address></record></records>",
        encoding="utf-8",
    )
    with pytest.raises(DataReadError):
        XmlReader().read(p)


def test_xml_empty_root_returns_empty(tmp_path: Path) -> None:
    p = tmp_path / "a.xml"
    p.write_text("<records></records>", encoding="utf-8")
    assert XmlReader().read(p) == []


def test_registry_returns_xml_reader(tmp_path: Path) -> None:
    p = tmp_path / "a.xml"
    p.write_text("<records></records>", encoding="utf-8")
    assert isinstance(get_reader(p), XmlReader)

# ---------- Excel ----------

def _make_xlsx(path: Path, rows: list[list]) -> None:
    wb = Workbook()
    ws = wb.active
    for r in rows:
        ws.append(r)
    wb.save(path)


def test_excel_basic(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    _make_xlsx(p, [["id", "name"], [1, "Иван"], [2, "Мария"]])
    rows = ExcelReader().read(p)
    assert rows == [
        {"id": 1, "name": "Иван"},
        {"id": 2, "name": "Мария"},
    ]


def test_excel_empty_cell_becomes_none(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    _make_xlsx(p, [["id", "name"], [1, None]])
    rows = ExcelReader().read(p)
    assert rows[0]["name"] is None


def test_excel_skips_fully_empty_rows(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    _make_xlsx(p, [["id", "name"], [1, "Иван"], [None, None], [2, "Мария"]])
    rows = ExcelReader().read(p)
    assert len(rows) == 2


def test_excel_named_sheet(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "first"
    ws1.append(["x"])
    ws1.append([1])
    ws2 = wb.create_sheet("data")
    ws2.append(["id"])
    ws2.append([42])
    wb.save(p)
    rows = ExcelReader(sheet_name="data").read(p)
    assert rows == [{"id": 42}]


def test_excel_missing_sheet_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    _make_xlsx(p, [["id"], [1]])
    with pytest.raises(DataReadError):
        ExcelReader(sheet_name="nope").read(p)


def test_excel_broken_file_raises(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    p.write_bytes(b"not an xlsx")
    with pytest.raises(DataReadError):
        ExcelReader().read(p)


def test_registry_returns_excel_reader(tmp_path: Path) -> None:
    p = tmp_path / "a.xlsx"
    _make_xlsx(p, [["id"], [1]])
    assert isinstance(get_reader(p), ExcelReader)
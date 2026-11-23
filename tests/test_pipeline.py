"""Интеграционные тесты: Reader -> Validator -> Converter -> Writer."""
from pathlib import Path

from readers.registry import read_file
from validators import load_schema, validate
from converters import load_convert_config
from writers.registry import get_writer


SCHEMA = """
fields:
  - name: id
    type: integer
    required: true
    unique: true
  - name: name
    type: string
    required: true
  - name: email
    type: string
    required: true
    pattern: "^[^@]+@[^@]+\\\\.[^@]+$"
  - name: age
    type: integer
    min: 16
    max: 100
mapping: {}
transforms:
  name: [trim]
  email: [trim, lower]
"""


def _write_config(tmp_path: Path) -> Path:
    p = tmp_path / "schema.yaml"
    p.write_text(SCHEMA, encoding="utf-8")
    return p


def test_full_pipeline_csv_to_json(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text(
        "id,name,email,age\n"
        "1,  Иван  ,IVAN@mail.ru,25\n"
        "2,Мария,maria@mail.ru,30\n"
        "3,Пётр,petr@mail.ru,200\n",
        encoding="utf-8",
    )
    cfg = _write_config(tmp_path)
    out = tmp_path / "out.json"

    rows = read_file(csv)
    result = validate(rows, load_schema(cfg))
    assert result.total == 3
    assert len(result.valid_rows) == 2
    assert result.invalid_count == 1

    converted = load_convert_config(cfg).apply(result.valid_rows)
    get_writer("json").write(converted, out)

    back = read_file(out)
    assert back == [
        {"id": "1", "name": "Иван", "email": "ivan@mail.ru", "age": "25"},
        {"id": "2", "name": "Мария", "email": "maria@mail.ru", "age": "30"},
    ]


def test_full_pipeline_csv_to_xlsx(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text("id,name\n1,Иван\n2,Мария\n", encoding="utf-8")
    cfg = tmp_path / "schema.yaml"
    cfg.write_text(
        "fields:\n"
        "  - name: id\n"
        "    type: integer\n"
        "  - name: name\n"
        "    type: string\n",
        encoding="utf-8",
    )
    out = tmp_path / "out.xlsx"

    rows = read_file(csv)
    result = validate(rows, load_schema(cfg))
    converted = load_convert_config(cfg).apply(result.valid_rows)
    get_writer("xlsx").write(converted, out)

    assert out.exists() and out.stat().st_size > 0
    back = read_file(out)
    assert len(back) == 2


def test_full_pipeline_mapping_and_transforms(tmp_path: Path) -> None:
    csv = tmp_path / "in.csv"
    csv.write_text("full_name,status\n  иван  ,active\n", encoding="utf-8")
    cfg = tmp_path / "schema.yaml"
    cfg.write_text(
        "fields:\n"
        "  - name: full_name\n"
        "    type: string\n"
        "  - name: status\n"
        "    type: string\n"
        "mapping:\n"
        "  full_name: name\n"
        "transforms:\n"
        "  name: [trim, upper]\n"
        "  status: [dict_replace]\n"
        "dict_replace:\n"
        "  status:\n"
        "    active: ACTIVE\n",
        encoding="utf-8",
    )

    rows = read_file(csv)
    result = validate(rows, load_schema(cfg))
    assert len(result.valid_rows) == 1

    converted = load_convert_config(cfg).apply(result.valid_rows)
    assert converted == [{"name": "ИВАН", "status": "ACTIVE"}]
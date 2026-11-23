"""Unit-тесты для converters."""
from datetime import datetime, timezone
from pathlib import Path

import pytest

from converters import (
    ConfigError,
    FieldMapper,
    Transformer,
    UpperCase,
    LowerCase,
    Trim,
    DictReplace,
    TimestampToDate,
    load_convert_config,
)


#  Трансформации: passthrough на не-str/None 

def test_upper_passes_none() -> None:
    assert UpperCase()(None) is None


def test_upper_passes_int() -> None:
    assert UpperCase()(25) == 25


def test_upper_on_string() -> None:
    assert UpperCase()("иван") == "ИВАН"


def test_lower_on_string() -> None:
    assert LowerCase()("ИВАН") == "иван"


def test_trim_on_string() -> None:
    assert Trim()("  иван  ") == "иван"


def test_trim_on_empty_string() -> None:
    assert Trim()("") == ""


#  DictReplace 

def test_dict_replace_hit() -> None:
    fn = DictReplace({"active": "ACTIVE"})
    assert fn("active") == "ACTIVE"


def test_dict_replace_miss() -> None:
    fn = DictReplace({"active": "ACTIVE"})
    assert fn("other") == "other"


def test_dict_replace_none() -> None:
    fn = DictReplace({"a": "b"})
    assert fn(None) is None


def test_dict_replace_non_dict_table_raises() -> None:
    from converters.base import TransformError
    with pytest.raises(TransformError):
        DictReplace("not a dict")  # type: ignore[arg-type]


#  TimestampToDate 

def test_timestamp_int() -> None:
    # 2024-05-01 00:00:00 UTC = 1714521600 -> dd.mm.yyyy
    assert TimestampToDate()(1714521600) == "01.05.2024"


def test_timestamp_float() -> None:
    assert TimestampToDate()(1714521600.0) == "01.05.2024"


def test_timestamp_string() -> None:
    assert TimestampToDate()("1714521600") == "01.05.2024"


def test_timestamp_bad_string_passthrough() -> None:
    assert TimestampToDate()("not-a-number") == "not-a-number"


def test_timestamp_none() -> None:
    assert TimestampToDate()(None) is None


def test_timestamp_bool_passthrough() -> None:
    assert TimestampToDate()(True) is True


#  FieldMapper 

def test_mapper_renames() -> None:
    m = FieldMapper({"full_name": "name"})
    got = m.apply([{"full_name": "Иван", "age": 25}])
    assert got == [{"name": "Иван", "age": 25}]


def test_mapper_does_not_mutate_input() -> None:
    rows = [{"full_name": "Иван"}]
    m = FieldMapper({"full_name": "name"})
    m.apply(rows)
    assert rows == [{"full_name": "Иван"}]


def test_mapper_identity_when_no_mapping() -> None:
    m = FieldMapper()
    got = m.apply([{"a": 1}])
    assert got == [{"a": 1}]


def test_mapper_duplicate_after_rename_raises() -> None:
    m = FieldMapper({"a": "b"})
    with pytest.raises(ConfigError):
        m.apply([{"a": 1, "b": 2}])


def test_mapper_non_string_keys_raises() -> None:
    with pytest.raises(ConfigError):
        FieldMapper({1: "x"})  # type: ignore[dict-item]


#  Transformer 

def test_transformer_applies_mapping_then_transforms() -> None:
    # mapping: full_name -> name, далее trim+upper по name
    t = Transformer(
        mapper=FieldMapper({"full_name": "name"}),
        transforms={"name": [Trim(), UpperCase()]},
    )
    got = t.apply([{"full_name": "  иван  "}])
    assert got == [{"name": "ИВАН"}]


def test_transformer_skips_missing_field() -> None:
    t = Transformer(transforms={"name": [UpperCase()]})
    got = t.apply([{"id": 1}])  # нет поля name
    assert got == [{"id": 1}]


def test_transformer_does_not_create_missing_field() -> None:
    t = Transformer(transforms={"name": [UpperCase()]})
    got = t.apply([{"id": 1}])
    assert "name" not in got[0]


def test_transformer_does_not_mutate_input() -> None:
    rows = [{"name": "  иван  "}]
    t = Transformer(transforms={"name": [Trim()]})
    t.apply(rows)
    assert rows == [{"name": "  иван  "}]


#  load_convert_config 

def _write_yaml(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "schema.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_load_config_full(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
mapping:
  full_name: name
transforms:
  name: [trim, upper]
  status: [dict_replace]
dict_replace:
  status:
    active: ACTIVE
""")
    t = load_convert_config(p)
    got = t.apply([{"full_name": "  иван  ", "status": "active"}])
    assert got == [{"name": "ИВАН", "status": "ACTIVE"}]


def test_load_config_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_convert_config(tmp_path / "nope.yaml")


def test_load_config_empty_yaml_returns_identity_transformer(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, "")
    t = load_convert_config(p)
    got = t.apply([{"a": 1}])
    assert got == [{"a": 1}]


def test_load_config_unknown_transform_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
transforms:
  name: [magic]
""")
    with pytest.raises(ConfigError):
        load_convert_config(p)


def test_load_config_dict_replace_without_table_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
transforms:
  status: [dict_replace]
""")
    with pytest.raises(ConfigError):
        load_convert_config(p)


def test_load_config_broken_yaml_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, "fields: [")
    with pytest.raises(ConfigError):
        load_convert_config(p)

def test_timestamp_bad_input_passthrough() -> None:
    assert TimestampToDate()("not-a-number") == "not-a-number"


def test_timestamp_none_passthrough() -> None:
    assert TimestampToDate()(None) is None
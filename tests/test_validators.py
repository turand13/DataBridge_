"""Unit-тесты для валидатора."""
from datetime import date, datetime
from pathlib import Path

import pytest

from validators import ConfigError, load_schema, validate
from validators.base import ValidationIssue, ValidationResult
from validators.rules import (
    RequiredRule,
    TypeRule,
    RangeRule,
    PatternRule,
    UniqueRule,
    LengthRule,
    _parse_date,
)


# ---------- _parse_date: 4 формата ----------

def test_parse_date_iso_dash() -> None:
    assert _parse_date("1999-01-15") == date(1999, 1, 15)


def test_parse_date_ru_dash() -> None:
    assert _parse_date("15-01-1999") == date(1999, 1, 15)


def test_parse_date_ru_dot() -> None:
    assert _parse_date("15.01.1999") == date(1999, 1, 15)


def test_parse_date_iso_dot() -> None:
    assert _parse_date("1999.01.15") == date(1999, 1, 15)


def test_parse_date_slash_rejected() -> None:
    assert _parse_date("15/01/1999") is None


def test_parse_date_not_a_date() -> None:
    assert _parse_date("not-a-date") is None


def test_parse_date_from_datetime() -> None:
    assert _parse_date(datetime(1999, 1, 15, 12, 30)) == date(1999, 1, 15)


def test_parse_date_from_date() -> None:
    assert _parse_date(date(1999, 1, 15)) == date(1999, 1, 15)


# ---------- RequiredRule ----------

def test_required_none_raises() -> None:
    assert RequiredRule("x").validate(None) == ["поле 'x' обязательно"]


def test_required_empty_string_ok() -> None:
    assert RequiredRule("x").validate("") == []


def test_required_value_ok() -> None:
    assert RequiredRule("x").validate("иван") == []


def test_required_false_disabled() -> None:
    assert RequiredRule("x", required=False).validate(None) == []


# ---------- TypeRule ----------

def test_type_integer_from_string() -> None:
    assert TypeRule("x", type="integer").validate("25") == []


def test_type_integer_from_int() -> None:
    assert TypeRule("x", type="integer").validate(25) == []


def test_type_integer_from_float_integral() -> None:
    assert TypeRule("x", type="integer").validate(25.0) == []


def test_type_integer_from_bad_string() -> None:
    assert TypeRule("x", type="integer").validate("abc") == [
        "поле 'x' должно быть integer"
    ]


def test_type_integer_none_skipped() -> None:
    assert TypeRule("x", type="integer").validate(None) == []


def test_type_date_iso() -> None:
    assert TypeRule("x", type="date").validate("1999-01-15") == []


def test_type_date_ru_dash() -> None:
    assert TypeRule("x", type="date").validate("15-01-1999") == []


def test_type_date_ru_dot() -> None:
    assert TypeRule("x", type="date").validate("15.01.1999") == []


def test_type_date_iso_dot() -> None:
    assert TypeRule("x", type="date").validate("1999.01.15") == []


def test_type_date_bad() -> None:
    assert TypeRule("x", type="date").validate("not-a-date") == [
        "поле 'x' должно быть date"
    ]


def test_type_boolean_from_true_string() -> None:
    assert TypeRule("x", type="boolean").validate("true") == []


def test_type_boolean_bad() -> None:
    assert TypeRule("x", type="boolean").validate("maybe") == [
        "поле 'x' должно быть boolean"
    ]


def test_type_unknown_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        TypeRule("x", type="magic")


# ---------- RangeRule: числа ----------

def test_range_number_in_bounds() -> None:
    assert RangeRule("age", min=16, max=100).validate("25") == []


def test_range_number_below_min() -> None:
    assert RangeRule("age", min=16, max=100).validate("17") == []


def test_range_number_at_min_boundary() -> None:
    assert RangeRule("age", min=16, max=100).validate("16") == []


def test_range_number_at_max_boundary() -> None:
    assert RangeRule("age", min=16, max=100).validate("100") == []


def test_range_number_above_max() -> None:
    assert RangeRule("age", min=16, max=100).validate("200") == [
        "поле 'age' больше максимума (100)"
    ]


def test_range_number_below_min_raises() -> None:
    assert RangeRule("age", min=16, max=100).validate("10") == [
        "поле 'age' меньше минимума (16)"
    ]


def test_range_number_non_numeric() -> None:
    assert RangeRule("age", min=16, max=100).validate("abc") == [
        "поле 'age' должно быть числом для проверки диапазона"
    ]


def test_range_requires_min_or_max() -> None:
    with pytest.raises(ConfigError):
        RangeRule("age")


# ---------- RangeRule: даты ----------

def test_range_date_in_bounds() -> None:
    assert RangeRule("d", min="2000-01-01", max="2010-12-31").validate("2005-06-15") == []


def test_range_date_before_min() -> None:
    assert RangeRule("d", min="2000-01-01", max="2010-12-31").validate("1999-12-31") == [
        "поле 'd' раньше минимума (2000-01-01)"
    ]


def test_range_date_after_max() -> None:
    assert RangeRule("d", min="2000-01-01", max="2010-12-31").validate("2011-01-01") == [
        "поле 'd' позже максимума (2010-12-31)"
    ]


def test_range_date_ru_format() -> None:
    assert RangeRule("d", min="01-01-2000", max="31-12-2010").validate("15-06-2005") == []


def test_range_date_bad_value() -> None:
    assert RangeRule("d", min="2000-01-01").validate("not-a-date") == [
        "поле 'd' не является датой для проверки диапазона"
    ]


# ---------- PatternRule ----------

def test_pattern_email_ok() -> None:
    assert PatternRule("email", pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$").validate(
        "ivan@mail.ru"
    ) == []


def test_pattern_email_no_at() -> None:
    assert PatternRule("email", pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$").validate(
        "maria.mail.ru"
    ) == ["поле 'email' не соответствует формату"]


def test_pattern_email_with_spaces() -> None:
    assert PatternRule("email", pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$").validate(
        " space@mail.ru "
    ) == ["поле 'email' не соответствует формату"]


def test_pattern_none_skipped() -> None:
    assert PatternRule("email", pattern=r".+").validate(None) == []


def test_pattern_bad_regex_raises_config_error() -> None:
    with pytest.raises(ConfigError):
        PatternRule("email", pattern="(")


# ---------- LengthRule ----------

def test_length_in_bounds() -> None:
    assert LengthRule("x", min_length=2, max_length=5).validate("abc") == []


def test_length_too_short() -> None:
    assert LengthRule("x", min_length=2).validate("a") == [
        "поле 'x' короче минимума (2)"
    ]


def test_length_too_long() -> None:
    assert LengthRule("x", max_length=2).validate("abc") == [
        "поле 'x' длиннее максимума (2)"
    ]


def test_length_none_skipped() -> None:
    assert LengthRule("x", min_length=2).validate(None) == []


def test_length_requires_param() -> None:
    with pytest.raises(ConfigError):
        LengthRule("x")


# ---------- UniqueRule (маркер) ----------

def test_unique_rule_validate_is_noop() -> None:
    assert UniqueRule("id").validate("1") == []


# ---------- load_schema ----------

def _write_yaml(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "schema.yaml"
    p.write_text(text, encoding="utf-8")
    return p


def test_load_schema_minimal(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
""")
    schema = load_schema(p)
    assert list(schema.keys()) == ["id"]
    assert len(schema["id"]) == 1


def test_load_schema_min_and_max_single_range_rule(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: age
    type: integer
    min: 16
    max: 100
""")
    schema = load_schema(p)
    range_rules = [r for r in schema["age"] if isinstance(r, RangeRule)]
    assert len(range_rules) == 1
    assert range_rules[0].min == 16
    assert range_rules[0].max == 100


def test_load_schema_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_schema(tmp_path / "nope.yaml")


def test_load_schema_broken_yaml_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, "fields: [")
    with pytest.raises(ConfigError):
        load_schema(p)


def test_load_schema_no_fields_key_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, "mapping:\n  a: b\n")
    with pytest.raises(ConfigError):
        load_schema(p)


def test_load_schema_empty_fields_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, "fields: []\n")
    with pytest.raises(ConfigError):
        load_schema(p)


def test_load_schema_field_without_rules_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
""")
    with pytest.raises(ConfigError):
        load_schema(p)


def test_load_schema_duplicate_field_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
  - name: id
    type: integer
""")
    with pytest.raises(ConfigError):
        load_schema(p)


def test_load_schema_unknown_type_raises(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: magic
""")
    with pytest.raises(ConfigError):
        load_schema(p)


def test_load_schema_ignores_convert_sections(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
mapping:
  full_name: name
transforms:
  name: [trim, upper]
dict_replace:
  status:
    active: ACTIVE
""")
    schema = load_schema(p)
    assert list(schema.keys()) == ["id"]


# ---------- validate(): на samples ----------

def _validate_sample(name: str) -> ValidationResult:
    schema = load_schema(Path("samples/schema.yaml"))
    from readers.registry import read_file
    rows = read_file(Path("samples") / name)
    return validate(rows, schema)


def test_validate_valid_csv() -> None:
    r = _validate_sample("valid.csv")
    assert (r.total, len(r.valid_rows), len(r.invalid_rows), r.errors_count) == (
        3, 3, 0, 0,
    )


def test_validate_valid_json() -> None:
    r = _validate_sample("valid.json")
    assert (r.total, len(r.valid_rows), len(r.invalid_rows), r.errors_count) == (
        3, 3, 0, 0,
    )


def test_validate_valid_xlsx() -> None:
    r = _validate_sample("valid.xlsx")
    assert (r.total, len(r.valid_rows), len(r.invalid_rows), r.errors_count) == (
        3, 3, 0, 0,
    )


def test_validate_valid_xml_has_two_records() -> None:
    r = _validate_sample("valid.xml")
    assert (r.total, len(r.valid_rows), len(r.invalid_rows), r.errors_count) == (
        2, 2, 0, 0,
    )


def test_validate_invalid_csv() -> None:
    r = _validate_sample("invalid.csv")
    # valid: 1, 6; invalid: 2,3,4,5,7,8,9,10; issues: 9
    assert (r.total, len(r.valid_rows), len(r.invalid_rows), r.errors_count) == (
        10, 2, 8, 9,
    )


def test_validate_invalid_csv_issues_fields() -> None:
    r = _validate_sample("invalid.csv")
    pairs = {(i.row_index, i.field) for i in r.issues}
    assert (2, "email") in pairs
    assert (3, "age") in pairs
    assert (4, "name") in pairs
    assert (5, "age") in pairs
    assert (7, "age") in pairs
    assert (8, "birth_date") in pairs
    assert (9, "id") in pairs
    assert (10, "email") in pairs


# ---------- validate(): ручные кейсы ----------

def test_validate_row_index_starts_at_one(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    type: integer
""")
    schema = load_schema(p)
    rows = [{"id": "1"}, {"id": "bad"}]
    r = validate(rows, schema)
    assert r.issues[0].row_index == 2


def test_validate_multiple_issues_per_row(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: age
    type: integer
    min: 16
    max: 100
""")
    schema = load_schema(p)
    r = validate([{"age": "abc"}], schema)
    # type + range
    assert r.errors_count == 2
    assert len(r.invalid_rows) == 1


def test_validate_unique_flags_second_occurrence(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    unique: true
""")
    schema = load_schema(p)
    rows = [{"id": "1"}, {"id": "1"}]
    r = validate(rows, schema)
    assert r.errors_count == 1
    assert r.issues[0].row_index == 2
    assert "уникаль" in r.issues[0].message


def test_validate_unique_skips_none(tmp_path: Path) -> None:
    p = _write_yaml(tmp_path, """
fields:
  - name: id
    unique: true
""")
    schema = load_schema(p)
    rows = [{"id": None}, {"id": None}]
    r = validate(rows, schema)
    assert r.errors_count == 0


def test_validate_empty_rows() -> None:
    schema = load_schema(Path("samples/schema.yaml"))
    r = validate([], schema)
    assert (r.total, len(r.valid_rows), len(r.invalid_rows), r.errors_count) == (
        0, 0, 0, 0,
    )


def test_validate_result_types() -> None:
    r = _validate_sample("valid.csv")
    assert isinstance(r, ValidationResult)
    assert all(isinstance(row, dict) for row in r.valid_rows)
    assert all(isinstance(i, ValidationIssue) for i in r.issues)
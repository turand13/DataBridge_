"""Unit-тесты для reporters: errors.csv и HTML-отчёт."""
import csv
from pathlib import Path

from readers.registry import read_file
from validators import load_schema, validate
from validators.base import ValidationIssue, ValidationResult
from reporters import write_errors_csv, write_html_report


# ---------- вспомогательные ----------

def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return reader.fieldnames or [], list(reader)


def _sample_result(name: str) -> ValidationResult:
    schema = load_schema(Path("samples/schema.yaml"))
    rows = read_file(Path("samples") / name)
    return validate(rows, schema)


# ---------- errors.csv ----------

def test_errors_csv_on_invalid_sample(tmp_path: Path) -> None:
    result = _sample_result("invalid.csv")

    out = tmp_path / "errors.csv"
    write_errors_csv(result, out)

    header, records = _read_csv(out)
    assert header[0] == "row_index"
    assert header[-1] == "errors"
    assert "id" in header and "email" in header

    by_index = {int(r["row_index"]): r for r in records}
    # невалидные: 2,3,4,5,7,8,9,10
    assert set(by_index) == {2, 3, 4, 5, 7, 8, 9, 10}

    assert "email" in by_index[2]["errors"]
    assert "age" in by_index[3]["errors"]
    assert "name" in by_index[4]["errors"]
    # у записи 5 две причины (type + range) в одной ячейке
    assert by_index[5]["errors"].count("age") >= 2
    assert "id" in by_index[9]["errors"]


def test_errors_csv_does_not_duplicate_rows(tmp_path: Path) -> None:
    result = _sample_result("invalid.csv")

    out = tmp_path / "errors.csv"
    write_errors_csv(result, out)
    _, records = _read_csv(out)

    # одна строка на невалидную запись
    assert len(records) == len(result.invalid_rows)
    indices = [int(r["row_index"]) for r in records]
    assert len(indices) == len(set(indices))


def test_errors_csv_empty_result_has_header(tmp_path: Path) -> None:
    result = _sample_result("valid.csv")

    out = tmp_path / "errors.csv"
    write_errors_csv(result, out)

    text = out.read_text(encoding="utf-8")
    assert text.strip() == "row_index,errors"


def test_errors_csv_manual_result(tmp_path: Path) -> None:
    result = ValidationResult(
        total=2,
        valid_rows=[],
        invalid_rows=[{"id": "1", "email": "bad"}, {"id": "2", "email": "x"}],
        invalid_row_indices=[1, 2],
        issues=[
            ValidationIssue(row_index=1, field="email", message="плохой"),
            ValidationIssue(row_index=1, field="id", message="тоже плохой"),
            ValidationIssue(row_index=2, field="email", message="ещё плохой"),
        ],
    )
    out = tmp_path / "errors.csv"
    write_errors_csv(result, out)
    header, records = _read_csv(out)

    assert header == ["row_index", "id", "email", "errors"]
    assert records[0]["row_index"] == "1"
    assert "email: плохой" in records[0]["errors"]
    assert "id: тоже плохой" in records[0]["errors"]
    assert "; " in records[0]["errors"]


# ---------- HTML-отчёт ----------

def test_html_report_on_invalid_sample(tmp_path: Path) -> None:
    result = _sample_result("invalid.csv")

    out = tmp_path / "report.html"
    write_html_report(result, out)

    html = out.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in html
    assert "Всего записей: <b>10</b>" in html
    assert 'Успешно обработано: <b class="ok">2</b>' in html
    assert 'Ошибок: <b class="err">9</b>' in html
    # есть таблица и колонки
    assert "<table>" in html
    assert "<th>Запись</th>" in html
    assert "<th>Поле</th>" in html
    assert "<th>Сообщение</th>" in html
    assert "email" in html


def test_html_report_no_errors(tmp_path: Path) -> None:
    result = _sample_result("valid.csv")

    out = tmp_path / "report.html"
    write_html_report(result, out)

    html = out.read_text(encoding="utf-8")
    assert 'Ошибок: <b class="err">0</b>' in html
    assert "Ошибок нет." in html
    assert "<table>" not in html


def test_html_report_escapes_html(tmp_path: Path) -> None:
    result = ValidationResult(
        total=1,
        valid_rows=[],
        invalid_rows=[{"x": "<script>"}],
        invalid_row_indices=[1],
        issues=[ValidationIssue(row_index=1, field="x", message="<b>bad</b>")],
    )
    out = tmp_path / "report.html"
    write_html_report(result, out)
    html = out.read_text(encoding="utf-8")
    assert "&lt;b&gt;bad&lt;/b&gt;" in html
    assert "<b>bad</b>" not in html
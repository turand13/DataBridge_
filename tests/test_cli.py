"""Тесты CLI: парсер, exit-коды, сквозные команды"""
from pathlib import Path

import pytest

from cli.main import main


SCHEMA_YAML = """
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
mapping: {}
transforms:
  name: [trim]
"""


def _write_csv(tmp_path: Path) -> Path:
    p = tmp_path / "in.csv"
    p.write_text(
        "id,name,email\n"
        "1,  Иван  ,ivan@mail.ru\n"
        "2,Мария,maria.mail.ru\n",  # email невалиден
        encoding="utf-8",
    )
    return p


def _write_config(tmp_path: Path) -> Path:
    p = tmp_path / "schema.yaml"
    p.write_text(SCHEMA_YAML, encoding="utf-8")
    return p


def test_parser_convert_required_args() -> None:
    from cli.main import build_parser
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["convert"])  


def test_convert_success(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path)
    cfg = _write_config(tmp_path)
    out = tmp_path / "out.json"
    code = main([
        "convert", str(csv),
        "--to", "json",
        "--config", str(cfg),
        "--output", str(out),
    ])
    assert code == 0
    assert out.exists()
    assert "Иван" in out.read_text(encoding="utf-8")


def test_convert_writes_errors_and_report(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path)
    cfg = _write_config(tmp_path)
    out = tmp_path / "out.json"
    err = tmp_path / "errors.csv"
    rep = tmp_path / "report.html"
    code = main([
        "convert", str(csv),
        "--to", "json", "--config", str(cfg),
        "--output", str(out), "--errors", str(err), "--report", str(rep),
    ])
    assert code == 0
    assert err.exists() and "maria.mail.ru" in err.read_text(encoding="utf-8")
    assert rep.exists() and "Отчёт" in rep.read_text(encoding="utf-8")


def test_convert_unknown_format_exits_2(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path)
    cfg = _write_config(tmp_path)
    with pytest.raises(SystemExit) as e:
        main([
            "convert", str(csv), "--to", "yaml",
            "--config", str(cfg), "--output", str(tmp_path / "o.yaml"),
        ])
    assert e.value.code == 2


def test_convert_missing_input_returns_1(tmp_path: Path) -> None:
    cfg = _write_config(tmp_path)
    code = main([
        "convert", str(tmp_path / "nope.csv"),
        "--to", "json", "--config", str(cfg),
        "--output", str(tmp_path / "o.json"),
    ])
    assert code == 1


def test_validate_success(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path)
    cfg = _write_config(tmp_path)
    rep = tmp_path / "report.html"
    code = main([
        "validate", str(csv),
        "--config", str(cfg), "--report", str(rep),
    ])
    assert code == 0
    assert rep.exists()


def test_validate_bad_config_returns_1(tmp_path: Path) -> None:
    csv = _write_csv(tmp_path)
    cfg = tmp_path / "bad.yaml"
    cfg.write_text("fields: [", encoding="utf-8")
    code = main(["validate", str(csv), "--config", str(cfg)])
    assert code == 1


def test_stats_success(tmp_path: Path, capsys) -> None:
    csv = _write_csv(tmp_path)
    code = main(["stats", str(csv)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Записей: 2" in out
    assert "Колонок: 3" in out
    assert "id" in out and "email" in out


def test_stats_empty_file(tmp_path: Path, capsys) -> None:
    p = tmp_path / "empty.csv"
    p.write_text("", encoding="utf-8")
    code = main(["stats", str(p)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Записей: 0" in out
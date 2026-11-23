#HTML-отчёт по результатам валидации

from datetime import datetime
from html import escape
from pathlib import Path

from validators import ValidationResult
from writers.base import DataWriteError

_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>DataBridge — отчёт о валидации</title>
<style>
  body {{ font-family: sans-serif; margin: 2rem; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
  th {{ background: #f0f0f0; }}
  .ok {{ color: #1a7f37; }}
  .err {{ color: #b42318; }}
</style>
</head>
<body>
<h1>Отчёт о валидации</h1>
<p>Сформирован: {generated}</p>
<ul>
  <li>Всего записей: <b>{total}</b></li>
  <li>Успешно обработано: <b class="ok">{valid}</b></li>
  <li>Ошибок: <b class="err">{errors}</b></li>
</ul>
{errors_block}
</body>
</html>
"""

_NO_ERRORS = '<p class="ok">Ошибок нет.</p>'

_ERRORS_TABLE = """<h2>Ошибки</h2>
<table>
<thead><tr><th>Запись</th><th>Поле</th><th>Сообщение</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>"""

_ROW = "<tr><td>{row_index}</td><td>{field}</td><td>{message}</td></tr>"


def write_html_report(result: ValidationResult, path: Path) -> None:
    #Сформировать report.html из ValidationResult.
    if result.issues:
        rows = "\n".join(
            _ROW.format(
                row_index=issue.row_index,
                field=escape(issue.field),
                message=escape(issue.message),
            )
            for issue in result.issues
        )
        errors_block = _ERRORS_TABLE.format(rows=rows)
    else:
        errors_block = _NO_ERRORS

    html = _TEMPLATE.format(
        generated=datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        total=result.total,
        valid=len(result.valid_rows),
        errors=result.errors_count,
        errors_block=errors_block,
    )
    try:
        path.write_text(html, encoding="utf-8")
    except OSError as e:
        raise DataWriteError(f"Не удалось записать {path.name}: {e}")
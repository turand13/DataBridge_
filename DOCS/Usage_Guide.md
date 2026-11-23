# Руководство по использованию

## Подготовка

1. `python -m venv .venv`
2. Активировать: `.venv\Scripts\activate` (Windows cmd) / `.venv\Scripts\Activate.ps1` (PowerShell) / `source .venv/bin/activate` (macOS/Linux).
3. `pip install -r requirements.txt`
4. `pip install -e .`

## 1. Статистика по файлу

`databridge stats samples/valid.csv`

Вывод: файл, число записей, число колонок, по каждой колонке — заполнено / пусто / уникальных. Схема не нужна.

## 2. Валидация с отчётом

`databridge validate samples/invalid.csv --config samples/schema.yaml --report samples/report.html --errors samples/errors.csv`

- `report.html` — статистика + таблица ошибок, открывается в браузере.
- `errors.csv` — невалидные записи с причинами.
- Код возврата `0`, даже если есть невалидные записи (валидация — не ошибка).

## 3. Конвертация CSV → JSON

`databridge convert samples/valid.csv --to json --config samples/schema.yaml --output samples/output.json`

Что происходит:

1. Reader читает CSV → `list[dict]`.
2. Validator проверяет по `fields` → `valid_rows`.
3. Converter применяет `mapping` + `transforms`.
4. Writer пишет JSON.
5. Консольная сводка (ТЗ 2.4).

## 4. Конвертация с отчётами

`databridge convert samples/invalid.csv --to xlsx --config samples/schema.yaml --output samples/output.xlsx --errors samples/errors.csv --report samples/report.html`

Невалидные записи не попадают в `output.xlsx`, а сохраняются в `errors.csv`.

## 5. Маппинг и трансформации

`samples/schema_map.yaml`:

- `fields`: `full_name` (string), `email` (string);
- `mapping`: `name: full_name`;
- `transforms`: `full_name: [trim, upper]`, `email: [trim, lower]`.

`databridge convert samples/map_in.csv --to csv --config samples/schema_map.yaml --output samples/map_out.csv`

Результат: колонка `full_name` (бывшая `name`), значения в верхнем регистре без пробелов; `email` в нижнем регистре.

> **Важно:** схема описывает **входные** имена (`full_name`), маппинг применяется после валидации. См. `DOCS/Architecture.md`, раздел 5.

## 6. Большие файлы

`python scripts/generate_samples.py`
`databridge stats samples/large_valid.csv`
`databridge convert samples/large_valid.csv --to json --config samples/schema.yaml --output samples/large_output.json`

1000 строк обрабатываются за доли секунды.

## 7. Ошибки

| Команда | Результат |
|---|---|
| `databridge stats samples/nope.csv` | `Ошибка: Файл не найден: ...`, код 1 |
| `databridge convert in.csv --to yaml ...` | argparse: недопустимый `--to`, код 2 |
| `databridge validate in.csv --config bad.yaml` | `Ошибка: Сломанный YAML ...`, код 1 |
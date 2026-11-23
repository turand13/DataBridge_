# Руководство пользователя

## 1. Установка

Требуется Python 3.10+.

1. `git clone <url> databridge && cd databridge`
2. Создать и активировать venv:
   - Windows cmd: `.venv\Scripts\activate`
   - PowerShell: `.venv\Scripts\Activate.ps1`
   - macOS/Linux: `source .venv/bin/activate`
3. `pip install -r requirements.txt`
4. `pip install -e .`

Проверка: `databridge --help` — должна показать список команд.

## 2. Команды

### `databridge stats <input>`

Статистика по файлу без схемы.

`databridge stats samples/valid.csv`

Вывод: файл, записей, колонок, таблица `Колонка / Заполнено / Пусто / Уникальных`.

### `databridge validate <input> --config <yaml> [--report <html>] [--errors <csv>]`

Чтение → валидация → отчёты.

`databridge validate samples/invalid.csv --config samples/schema.yaml --report samples/report.html --errors samples/errors.csv`

- `--config` — обязателен.
- `--report` — HTML-отчёт (необязательно).
- `--errors` — `errors.csv` (необязательно).

Код возврата: `0` (даже если есть невалидные записи), `1` — ошибка данных/конфига.

### `databridge convert <input> --to <fmt> --config <yaml> --output <path> [--report <html>] [--errors <csv>]`

Чтение → валидация → конвертация → запись.

`databridge convert samples/valid.csv --to json --config samples/schema.yaml --output samples/output.json`

- `--to` — `csv`, `json`, `xml`, `xlsx` (алиас `excel`).
- `--config` — обязателен.
- `--output` — обязателен.
- `--report`/`--errors` — необязательны.

Код возврата: `0` — успех, `1` — ошибка данных/конфига, `2` — недопустимый аргумент (argparse).

## 3. Формат конфига

- `fields`: `id` (integer, required, unique), `email` (string, required, pattern), `age` (integer, min 16, max 100).
- `mapping`: `full_name: name`.
- `transforms`: `name: [trim, upper]`, `email: [trim, lower]`.
- `dict_replace`: пустой или словари замен.

Подробно — `Config_Spec.md`.

## 4. Форматы данных

| Формат | Чтение | Запись |
|---|---|---|
| CSV | заголовки / без, разделитель | заголовки, объединение ключей |
| JSON | массив объектов | массив объектов, `ensure_ascii=False` |
| XML | плоская структура | `<records><record>...` |
| XLSX | первый лист / по имени | первый лист, формат дат `DD.MM.YYYY` |

## 5. Даты

- `date` → `dd.mm.yyyy` (CSV, JSON, XML, Excel-отображение).
- `datetime` → ISO 8601 (`YYYY-MM-DDTHH:MM:SS`), чтобы не терять время.
- `timestamp_to_date` → `dd.mm.yyyy`.

## 6. Ошибки и коды возврата

| Код | Значение |
|---|---|
| 0 | Успех |
| 1 | Ошибка данных/конфига (`DataReadError`, `DataWriteError`, `ConfigError`) |
| 2 | Ошибка аргументов (argparse) |
| 3 | Внутренняя ошибка |

Сообщения — в stderr, без traceback.

## 7. Примеры «до/после»

См. `samples/`: `valid.csv` → `output.json`, `invalid.csv` → `errors.csv` + `report.html`, `map_in.csv` → `map_out.csv` (маппинг + трансформации).

## 8. Частые проблемы

| Проблема | Решение |
|---|---|
| `databridge: command not found` | Активируй venv, `pip install -e .` |
| Даты в ISO вместо `dd.mm.yyyy` | Для CSV-строк конвертация дат не применяется — нужен `datetime`/`date` или `timestamp_to_date` |
| Маппинг «не сработал» | Схема — входные имена, `mapping` — после валидации |
| Excel-файл занят | Закрой его в Excel перед записью |
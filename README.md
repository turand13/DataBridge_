# DataBridge

Утилита командной строки для чтения, валидации и конвертации табличных данных
между форматами **CSV, JSON, XML и Excel (.xlsx)**.

## Что умеет

- **Чтение** из CSV (с заголовками и без, настраиваемый разделитель), JSON
  (массив объектов), XML (плоская структура), Excel (.xlsx).
  Формат определяется по расширению файла.
- **Валидация** по правилам из YAML-конфига: `required`, `type`
  (`integer`/`float`/`string`/`date`/`boolean`), `min`/`max`, `pattern`,
  `unique`, `min_length`/`max_length`.
- **Конвертация**: чтение из любого формата → запись в любой; маппинг полей;
  трансформации (`upper`, `lower`, `trim`, `dict_replace`, `timestamp_to_date`).
- **Отчёты**: `errors.csv` с некорректными записями и причинами,
  `report.html` со статистикой и таблицей ошибок.
- **CLI**: команды `convert`, `validate`, `stats`.

## Установка

Требуется Python 3.10+.

```bash
git clone https://github.com/turand13/DataBridge_ databridge
cd databridge

python -m venv .venv
# Windows (cmd):
.venv\Scripts\activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
pip install -e .
```
## Быстрый старт
```
databridge stats samples/valid.csv

databridge validate samples/invalid.csv \
    --config samples/schema.yaml \
    --report samples/report.html \
    --errors samples/errors.csv

databridge convert samples/valid.csv \
    --to json \
    --config samples/schema.yaml \
    --output samples/output.json
```
## Команды CLI
```
databridge convert <input> --to <fmt> --config <yaml> --output <path>  -  чтение → валидация → конвертация → запись; опционально --report, --errors

databridge validate <input> --config <yaml>  -  чтение → валидация → отчёты; опционально --report, --errors

databridge stats <input>  -  статистика по файлу без схемы
```
Целевые форматы для --to: csv, json, xml, xlsx

## Формат конфига

Один YAML-файл содержит секции валидатора и конвертера:
```
fields:
  - name: id
    type: integer
    required: true
    unique: true
  - name: email
    type: string
    required: true
    pattern: "^[^@]+@[^@]+\\.[^@]+$"
  - name: age
    type: integer
    min: 16
    max: 100

mapping:
  full_name: name

transforms:
  name: [trim, upper]
  email: [trim, lower]
  status: [dict_replace]

dict_replace:
  status:
    active: ACTIVE
    inactive: INACTIVE
```
Подробнее - DOCS/Config_Spec.md.

## Тесты
```
pytest -q
```
## Документация

DOCS/Requirements.md — функциональные требования

DOCS/Architecture.md — модули и поток данных

DOCS/Config_Spec.md — спецификация конфига

DOCS/Usage_Guide.md — сценарии использования

DOCS/Test_Plan.md — тестовые сценарии

DOCS/Test_Report.md — результаты прогона и дефекты

DOCS/User_Manual.md — установка, все команды, примеры

## Ограничения

Все данные читаются в память (list[dict]). Для ~1 млн строк нужен стриминг.

XML — только плоская структура.

JSON — только массив объектов.


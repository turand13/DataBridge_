# План тестирования

## Подход

- **Unit-тесты** (`pytest`) — каждый слой отдельно.
- **Интеграционные тесты** — сквозные сценарии Reader → Validator → Converter → Writer.
- **Ручные сценарии** — прогон команд CLI на `samples/`, проверка `output.*`, `errors.csv`, `report.html`.

Запуск: `pytest -q`.

## Unit-тесты по слоям

### Readers

CSV: заголовок, без заголовка, настраиваемый разделитель, BOM, пустое поле → `None`, пустой файл / только заголовок, битая кодировка → `DataReadError`. JSON: массив объектов, пустой массив, битый JSON, корень не массив, элемент не объект, `null` → `None`. XML: плоская структура, пустой тег → `None`, битый XML, вложенный тег → `DataReadError`. Excel: базовое чтение, пустая ячейка → `None`, пропуск пустых строк, именованный лист / отсутствующий лист, битый файл (`BadZipFile`) → `DataReadError`. Реестр: выбор по расширению, неизвестное расширение.

### Writers

CSV: запись, `None` → пусто, объединение ключей, пустой набор → пустой файл, несуществующая папка → `DataWriteError`. JSON: кириллица (`ensure_ascii=False`), `date` → `dd.mm.yyyy`, `datetime` → ISO. XML: корень `<records>`, пустой тег для `None`. Excel: запись, `datetime` round-trip, формат дат. Реестр: `get_writer` для всех форматов, алиас `excel`, неизвестный → `DataWriteError`. Round-trip: write → read → equals (csv/json/xml/xlsx).

### Validators

Все правила: `required`, `type` (все типы), `min`/`max` (числа и даты), `pattern`, `unique`, `min_length`/`max_length`. `None` vs `""` — разная трактовка. `unique`: дубликаты, `None` не участвует. `load_schema`: битый YAML, нет `fields`, дубликат поля, поле без правил. `validate` на `samples/invalid.csv`: согласованность `invalid_rows`/`invalid_row_indices`/`issues`.

### Converters

`upper`/`lower`/`trim`: строки, `None`, числа (passthrough). `dict_replace`: hit/miss/`None`/не-dict. `timestamp_to_date`: int/float/строка, битые значения (passthrough). `FieldMapper`: переименование, отсутствие мутации, дубликат → `ConfigError`. `Transformer`: mapping → transforms, отсутствующее поле не создаётся. `load_convert_config`: полный конфиг, пустой YAML, неизвестная трансформация, `dict_replace` без словаря, битый YAML.

### CLI

`--help` и справка подкоманд. `convert`: успех, `--errors`/`--report`, недопустимый `--to` (код 2), отсутствующий вход (код 1). `validate`: успех, битый конфиг (код 1). `stats`: успех, пустой файл.

### Reporters

`errors.csv`: невалидные записи, причины через `; `, нет дублей. `report.html`: статистика, таблица ошибок, «Ошибок нет».

### Интеграционные

CSV → validate → convert → JSON. CSV → validate → convert → XLSX. mapping + transforms в сквозном сценарии.

## Ручные сценарии

1. `stats valid.csv` — 3 записи, 5 колонок, код 0.
2. `stats nope.csv` — сообщение, код 1.
3. `validate invalid.csv` — сводка, `errors.csv`, `report.html`.
4. `report.html` открывается в браузере, таблица ошибок.
5. `validate valid.csv` — «Ошибок: 0».
6. `validate` с битым конфигом — сообщение, код 1.
7. `convert` CSV→JSON — trim/lower, даты `dd.mm.yyyy`.
8. `convert` CSV→XLSX — открывается в Excel, формат дат.
9. `convert` JSON→XML — корень `<records>`, кириллица.
10. `convert` с маппингом — переименование, трансформации.
11. `convert --errors` — только невалидные.
12. `convert --to yaml` — код 2.
13. `convert` с несуществующим входом — код 1.
14. Большие файлы (1000 строк) — все форматы, < 2 с.

## Критерии приёмки

- `pytest -q` — все тесты зелёные.
- Все ручные сценарии проходят.
- Нет traceback для ожидаемых ошибок.
- Коды возврата соответствуют таблице.
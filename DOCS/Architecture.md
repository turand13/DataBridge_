# Архитектура — DataBridge

## 1. Схема потока данных

Поток: `Reader → Validator → Converter → Writer`. Reporter'ы подключаются по флагам `--errors`/`--report`. Оркестрация — в `cli/`.

## 2. Модули

| Пакет | Ответственность | Ключевые сущности |
|---|---|---|
| `readers/` | файл → `list[dict]` | `Reader`, `CsvReader`, `JsonReader`, `XmlReader`, `ExcelReader`, `read_file()` |
| `writers/` | `list[dict]` → файл | `Writer`, `CsvWriter`, `JsonWriter`, `XmlWriter`, `ExcelWriter`, `get_writer()` |
| `validators/` | проверка по схеме | `Rule`, `validate()`, `load_schema()`, `ValidationResult` |
| `converters/` | маппинг + трансформации | `FieldMapper`, `Transformer`, `load_convert_config()` |
| `reporters/` | отчёты | `write_errors_csv()`, `write_html_report()` |
| `cli/` | команды | `main()`, `build_parser()`, команды `convert`/`validate`/`stats` |

## 3. Контракты между слоями

### Reader
`read(path: Path) -> list[dict[str, Any]]`. Ключи — имена колонок, пустые значения — `None`, ошибки — `DataReadError`, выбор по расширению — `read_file()`.

### Validator
`load_schema(path: Path) -> dict[str, list[Rule]]` и `validate(rows, schema) -> ValidationResult`.

`ValidationResult`: `total`, `valid_rows`, `invalid_rows`, `invalid_row_indices` (параллельный `invalid_rows`), `issues`, `errors_count`, `invalid_count`.

Валидатор типы не приводит; `invalid_rows[i]` соответствует номеру `invalid_row_indices[i]`.

### Converter
`load_convert_config(path: Path) -> Transformer` и `transformer.apply(rows) -> list[dict]`.

Порядок: сначала `mapping`, затем `transforms`. Трансформации устойчивы к типу: `None` и не-строки проходят без изменений. Входные данные не мутируются.

### Writer
`write(rows, path) -> None`. `None` → пустое значение формата, `date` → `dd.mm.yyyy`, `datetime` → ISO 8601. Ошибки — `DataWriteError`. Выбор по имени формата — `get_writer()`.

### Reporter
`write_errors_csv(result, path)` и `write_html_report(result, path)`.

## 4. Добавление нового формата

1. Класс в `readers/` (`extensions = (".yaml",)`).
2. Класс в `writers/`.
3. Строка в `readers/registry._READERS` и `writers/registry._WRITERS`.
4. Остальной код (CLI, валидатор, конвертер) не меняется.

## 5. Важное архитектурное решение: mapping vs validation

Валидатор видит **входные** имена полей. Маппинг применяется **после** валидации, к валидным записям. Поэтому:

- схема валидатора описывает **исходные** имена (`full_name`, `e_mail`);
- `mapping` переименовывает их **на выходе** (`full_name → name`);
- `transforms` задаются по **новым** именам (после маппинга).

Альтернатива — Converter **до** Validator — отклонена: тогда ошибки в `errors.csv` были бы по переименованным полям, что противоречит ТЗ (валидация перед конвертацией) и усложняет отладку.

Пример:

- `fields`: `name: full_name` (входное имя).
- `mapping`: `full_name: name`.
- `transforms`: `name: [trim, upper]` (по выходному имени).

## 6. Обработка ошибок

| Слой | Исключение | Кто ловит |
|---|---|---|
| Reader | `DataReadError` | `cli/errors.run_with_errors` |
| Writer | `DataWriteError` | то же |
| Validator/Converter | `ConfigError` | то же |
| argparse | `SystemExit(2)` | сам argparse |

CLI печатает `Ошибка: <текст>` в stderr и возвращает код `1`. Непредвиденные — код `3` с текстом `Внутренняя ошибка: ...`. Никаких traceback для ожидаемых ошибок.

## 7. Производительность и масштабирование

- Все данные — в памяти (`list[dict]`). 1000 строк — доли секунды.
- Оценка на 1 млн строк: ~500 МБ–1 ГБ RAM, поэтому нужен стриминг: CSV — `csv.reader` построчно, JSON — `ijson`, XML — `iterparse`, Excel — `openpyxl read_only=True` (уже включён).
- Архитектура `Reader`/`Writer` допускает замену `read()` на `iter_rows()` без изменения остальных слоёв.
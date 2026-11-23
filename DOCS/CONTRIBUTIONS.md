# Вклад участников

## <Турланов А.В.>

- `readers/` — CSV, JSON, XML, Excel Reader'ы, реестр, `DataReadError`.
- `writers/` — CSV, JSON, XML, Excel Writer'ы, нормализация значений, реестр.
- `converters/` — `FieldMapper`, `Transformer`, 5 трансформаций, `load_convert_config`.
- `cli/` — `main.py`, `errors.py`, `summary.py`, команды `convert`/`validate`/`stats`.
- `scripts/generate_samples.py` — генератор 1000+ строк.
- Тесты: `test_readers.py`, `test_writers.py`, `test_converters.py`, `test_cli.py`, `test_pipeline.py`.
- Документация: `Architecture.md`, `Config_Spec.md`, `Usage_Guide.md`.

## <Сафиуллин Г.Э.>

- `validators/` — движок валидации, правила (`required`, `type`, `min`/`max`, `pattern`, `unique`, `min_length`/`max_length`), `load_schema`, `ValidationResult`.
- `reporters/` — `write_errors_csv`, `write_html_report`.
- Тесты: `test_validators.py`, `test_reporters.py`.
- Документация: `Requirements.md`, `Test_Plan.md`, `Test_Report.md`, `User_Manual.md`.
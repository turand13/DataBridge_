# Спецификация конфигурационного файла

Один YAML-файл содержит секции валидатора (`fields`) и конвертера (`mapping`, `transforms`, `dict_replace`). Секции независимы: `fields` читает `validators.load_schema`, остальные — `converters.load_convert_config`.

## 1. Секция `fields` (валидация)

| Ключ | Тип | Описание |
|---|---|---|
| `name` | строка | имя поля (обязательно) |
| `type` | `integer`/`float`/`string`/`date`/`boolean` | проверка приводимости к типу |
| `required` | bool | поле не `None` |
| `unique` | bool | уникальность в наборе; `None` не участвует |
| `min`/`max` | число или дата | диапазон |
| `pattern` | строка (regex) | полное совпадение (`fullmatch`) |
| `min_length`/`max_length` | целое | длина строки |
| `format` | строка | зарезервировано, пока не используется |

Правила: `min`+`max` → один `RangeRule`; `min_length`+`max_length` → один `LengthRule`. Поле без единого правила → `ConfigError`.

## 2. Секция `mapping` (переименование)

`{входное_имя: выходное_имя}`. Применяется **после** валидации, поэтому `fields` описывает **входные** имена. Дубликат после переименования → `ConfigError`.

## 3. Секция `transforms` (трансформации)

`{поле: [имена_трансформаций]}` — цепочка применяется по порядку. Поле — **выходное** имя (после `mapping`). Если поля нет в записи — трансформация пропускается (поле не создаётся).

| Имя | Что делает | Применимо к |
|---|---|---|
| `upper` | верхний регистр | строки; `None`/числа — passthrough |
| `lower` | нижний регистр | строки; `None`/числа — passthrough |
| `trim` | обрезка пробелов | строки; `None`/числа — passthrough |
| `dict_replace` | замена по словарю `dict_replace[поле]` | любой тип |
| `timestamp_to_date` | UNIX timestamp → `dd.mm.yyyy` | int/float/строка с числом |

## 4. Секция `dict_replace` (словари замен)

`{поле: {исходное: новое}}`. Нужна, если в `transforms` для поля указан `dict_replace`; иначе `ConfigError`.

## 5. Полный пример

```yaml
fields:
  - name: id
    type: integer
    required: true
    unique: true
  - name: full_name
    type: string
    required: true
    min_length: 1
  - name: e_mail
    type: string
    required: true
    pattern: "^[^@]+@[^@]+\\.[^@]+$"
  - name: age
    type: integer
    min: 16
    max: 100
  - name: status
    type: string

mapping:
  full_name: name
  e_mail: email

transforms:
  name: [trim, upper]
  email: [trim, lower]
  status: [dict_replace]

dict_replace:
  status:
    active: ACTIVE
    inactive: INACTIVE

## 6. Ошибки конфига

Файл не найден / не UTF-8 / битый YAML;

Нет корневого fields / fields пуст;

Поле без name или с дубликатом name;

Неизвестный type / трансформация / правило;

Dict_replace указан в transforms, но словаря нет;

Min/max/min_length/max_length — не целое;

Дубликат ключа после mapping.


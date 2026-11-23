from pathlib import Path
from typing import Any

import yaml

from .base import Rule, ConfigError
from .registry import get_rule


def load_schema(path: Path) -> dict[str, list[Rule]]:
    #Прочитать YAML-конфиг и вернуть {имя_поля: [правила]}

    if not path.exists():
        raise ConfigError(f"Файл конфигурации не найден: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        raise ConfigError(f"Конфиг {path.name} не в UTF-8. Проверьте кодировку.")
    except yaml.YAMLError as e:
        raise ConfigError(f"Сломанный YAML в {path.name}: {e}")

    if not isinstance(raw, dict) or "fields" not in raw:
        raise ConfigError(
            f"Конфиг {path.name}: ожидается корневой ключ 'fields' со списком полей"
        )

    fields = raw["fields"]
    if not isinstance(fields, list) or not fields:
        raise ConfigError(
            f"Конфиг {path.name}: 'fields' должен быть непустым списком"
        )

    schema: dict[str, list[Rule]] = {}
    for i, item in enumerate(fields, start=1):
        name, rules = _parse_field(item, index=i, source=path.name)
        if name in schema:
            raise ConfigError(
                f"Конфиг {path.name}: поле '{name}' описано более одного раза"
            )
        schema[name] = rules
    return schema


def _parse_field(
    item: Any, index: int, source: str
) -> tuple[str, list[Rule]]:
    #Разобрать одно поле конфига в (имя, список правил).
    if not isinstance(item, dict):
        raise ConfigError(
            f"Конфиг {source}: элемент fields[{index}] должен быть словарём"
        )
    name = item.get("name")
    if not isinstance(name, str) or not name:
        raise ConfigError(
            f"Конфиг {source}: в fields[{index}] отсутствует или пустое 'name'"
        )

    rules: list[Rule] = []

    # По одному правилу на ключ.
    if "type" in item:
        rules.append(get_rule("type", name, {"type": item["type"]}))

    range_params: dict[str, Any] = {}
    if "min" in item:
        range_params["min"] = _as_int(item["min"], "min", name, source)
    if "max" in item:
        range_params["max"] = _as_int(item["max"], "max", name, source)
    if range_params:
        rules.append(get_rule("range", name, range_params))

    if "pattern" in item:
        if not isinstance(item["pattern"], str):
            raise ConfigError(
                f"Конфиг {source}: поле '{name}', 'pattern' должен быть строкой"
            )
        rules.append(get_rule("pattern", name, {"pattern": item["pattern"]}))

    if "unique" in item:
        rules.append(get_rule("unique", name, {"unique": bool(item["unique"])}))

    length_params: dict[str, Any] = {}
    if "min_length" in item:
        length_params["min_length"] = _as_int(
            item["min_length"], "min_length", name, source
        )
    if "max_length" in item:
        length_params["max_length"] = _as_int(
            item["max_length"], "max_length", name, source
        )
    if length_params:
        rules.append(get_rule("length", name, length_params))

    if "required" in item:
        rules.append(get_rule("required", name, {"required": bool(item["required"])}))

    if not rules:
        raise ConfigError(
            f"Конфиг {source}: у поля '{name}' не задано ни одного правила"
        )
    return name, rules


def _as_int(value: Any, key: str, field: str, source: str) -> int:
    #Проверить, что параметр — целое число (не bool)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError(
            f"Конфиг {source}: поле '{field}', '{key}' должен быть целым числом"
        )
    return value
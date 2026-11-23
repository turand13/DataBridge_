"""Загрузка секции конвертации из YAML (mapping, transforms, dict_replace)"""
from pathlib import Path
from typing import Any, Callable

import yaml

from .base import ConfigError
from .mapper import FieldMapper
from .pipeline import Transformer
from .transforms import (
    UpperCase,
    LowerCase,
    Trim,
    DictReplace,
    TimestampToDate,
)


# Реестр трансформаций по имени в конфиге
# Добавление новой трансформации = строка в этом словаре
_SIMPLE_TRANSFORMS: dict[str, Callable[[], Callable[[Any], Any]]] = {
    "upper": UpperCase,
    "lower": LowerCase,
    "trim": Trim,
    "timestamp_to_date": TimestampToDate,
}


def load_convert_config(path: Path) -> Transformer:
    """Прочитать YAML и вернуть готовый Transformer

    Если секций mapping/transforms в файле нет, то вернуть пустой Transformer,
    который просто копирует записи"""
    if not path.exists():
        raise ConfigError(f"Файл конфигурации не найден: {path}")

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        raise ConfigError(f"Конфиг {path.name} не в UTF-8. Проверьте кодировку.")
    except yaml.YAMLError as e:
        raise ConfigError(f"Сломанный YAML в {path.name}: {e}")

    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ConfigError(f"Конфиг {path.name}: корень должен быть словарём")

    mapping = raw.get("mapping") or {}
    mapper = FieldMapper(mapping)

    dict_replace_tables = raw.get("dict_replace") or {}
    transforms_cfg = raw.get("transforms") or {}

    if not isinstance(transforms_cfg, dict):
        raise ConfigError(
            f"Конфиг {path.name}: 'transforms' должен быть словарём "
            f"{{поле: [имена трансформаций]}}"
        )

    transforms: dict[str, list[Callable[[Any], Any]]] = {}
    for field, chain in transforms_cfg.items():
        if not isinstance(field, str):
            raise ConfigError(
                f"Конфиг {path.name}: имена полей в 'transforms' должны быть строками"
            )
        if not isinstance(chain, list) or not chain:
            raise ConfigError(
                f"Конфиг {path.name}: transforms['{field}'] должен быть непустым списком"
            )
        transforms[field] = [
            _build_transform(name, dict_replace_tables, field, path.name)
            for name in chain
        ]

    return Transformer(mapper=mapper, transforms=transforms)


def _build_transform(
    name: Any,
    dict_replace_tables: dict[str, Any],
    field: str,
    source: str,
) -> Callable[[Any], Any]:
    """Создать экземпляр трансформации по имени из конфига"""
    if not isinstance(name, str):
        raise ConfigError(
            f"Конфиг {source}: transforms['{field}'] содержит не строку: {name!r}"
        )
    if name == "dict_replace":
        if field not in dict_replace_tables:
            raise ConfigError(
                f"Конфиг {source}: для поля '{field}' нужна трансформация "
                f"'dict_replace', но секция dict_replace['{field}'] не задана"
            )
        table = dict_replace_tables[field]
        if not isinstance(table, dict):
            raise ConfigError(
                f"Конфиг {source}: dict_replace['{field}'] должен быть словарём"
            )
        return DictReplace(table)

    if name in _SIMPLE_TRANSFORMS:
        return _SIMPLE_TRANSFORMS[name]()

    available = ", ".join(sorted(list(_SIMPLE_TRANSFORMS) + ["dict_replace"]))
    raise ConfigError(
        f"Конфиг {source}: неизвестная трансформация '{name}' для поля '{field}'. "
        f"Доступно: {available}"
    )
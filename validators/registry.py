from typing import Any

from .base import Rule, ConfigError
from . import rules as _rules


# Реестр всех зарегистрированных правил
_RULES: list[type[Rule]] = [
    _rules.RequiredRule,
    _rules.TypeRule,
    _rules.RangeRule,
    _rules.PatternRule,
    _rules.UniqueRule,
    _rules.LengthRule,
]


def get_rule(rule_type: str, field_name: str, params: dict[str, Any]) -> Rule:
    #Создать правило по типу, имени поля и параметрам из конфига
    for rule_cls in _RULES:
        if rule_cls.rule_type == rule_type:
            return rule_cls(field_name=field_name, **params)

    available = ", ".join(r.rule_type for r in _RULES)
    raise ConfigError(
        f"Неизвестное правило '{rule_type}' для поля '{field_name}'. "
        f"Доступно: {available}"
    )


def available_rules() -> list[str]:
    #Список поддерживаемых типов правил (для подсказок/документации)
    return [r.rule_type for r in _RULES]
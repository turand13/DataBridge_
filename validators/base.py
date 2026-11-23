from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class ConfigError(Exception):
    # Ошибка конфигурации валидатора
    pass


@dataclass
class ValidationIssue:
    # Одна проблема валидации по конкретной записи и полю
    row_index: int
    field: str
    message: str


@dataclass
class ValidationResult:
    # Итог валидации набора записей.
    total: int
    valid_rows: list[dict[str, Any]] = field(default_factory=list)
    invalid_rows: list[dict[str, Any]] = field(default_factory=list)
    invalid_row_indices: list[int] = field(default_factory=list)
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors_count(self) -> int:
        # Количество найденных проблем
        return len(self.issues)

    @property
    def invalid_count(self) -> int:
        # Количество записей, не прошедших валидацию
        return len(self.invalid_rows)


class Rule(ABC):
    # Абстрактное правило проверки одного поля.
    rule_type: str = ""

    def __init__(self, field_name: str) -> None:
        self.field_name = field_name

    @abstractmethod
    def validate(self, value: Any) -> list[str]:
        ...

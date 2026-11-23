from typing import Any

from .base import Rule, ValidationIssue, ValidationResult
from .rules import UniqueRule


def validate(
    rows: list[dict[str, Any]],
    schema: dict[str, list[Rule]],
) -> ValidationResult:
    #Провалидировать записи по схеме.
    result = ValidationResult(total=len(rows))

    # Разделяем правила на построчные и наборные (unique).
    row_rules, unique_rules = _split_rules(schema)

    # Построчные проверки. Копим issues по индексу записи.
    issues_by_row: dict[int, list[ValidationIssue]] = {}
    for row_index, row in enumerate(rows, start=1):
        for field_name, rules in row_rules.items():
            value = row.get(field_name)
            for rule in rules:
                for message in rule.validate(value):
                    issues_by_row.setdefault(row_index, []).append(
                        ValidationIssue(
                            row_index=row_index,
                            field=field_name,
                            message=message,
                        )
                    )

    # Наборные проверки unique.
    if unique_rules:
        _check_unique(rows, unique_rules, issues_by_row)

    # Разложить записи на валидные/невалидные по наличию issues.
    for row_index, row in enumerate(rows, start=1):
        row_issues = issues_by_row.get(row_index, [])
        if row_issues:
            result.invalid_rows.append(row)
            result.invalid_row_indices.append(row_index)
            result.issues.extend(row_issues)
        else:
            result.valid_rows.append(row)

    return result


def _split_rules(
    schema: dict[str, list[Rule]],
) -> tuple[dict[str, list[Rule]], dict[str, list[UniqueRule]]]:
    #Разделить правила схемы на построчные и unique.
    row_rules: dict[str, list[Rule]] = {}
    unique_rules: dict[str, list[UniqueRule]] = {}

    for field_name, rules in schema.items():
        for rule in rules:
            if isinstance(rule, UniqueRule):
                unique_rules.setdefault(field_name, []).append(rule)
            else:
                row_rules.setdefault(field_name, []).append(rule)
    return row_rules, unique_rules


def _check_unique(
    rows: list[dict[str, Any]],
    unique_rules: dict[str, list[UniqueRule]],
    issues_by_row: dict[int, list[ValidationIssue]],
) -> None:
    #Наборная проверка уникальности: помечаем все дубликаты, кроме первого.

    for field_name, rules in unique_rules.items():
        active = any(rule.unique for rule in rules)
        if not active:
            continue

        seen: dict[Any, int] = {}  
        for row_index, row in enumerate(rows, start=1):
            value = row.get(field_name)
            if value is None:
                continue  
            if value in seen:
                first = seen[value]
                issues_by_row.setdefault(row_index, []).append(
                    ValidationIssue(
                        row_index=row_index,
                        field=field_name,
                        message=(
                            f"поле '{field_name}' должно быть уникальным "
                            f"(повтор значения из записи {first})"
                        ),
                    )
                )
            else:
                seen[value] = row_index

"""Оркестратор преобразования: mapping -> transforms"""
from typing import Any, Callable

from .base import ConfigError
from .mapper import FieldMapper


class Transformer:
    """Применяет маппинг полей и цепочки трансформаций к записям."""

    def __init__(
        self,
        mapper: FieldMapper | None = None,
        transforms: dict[str, list[Callable[[Any], Any]]] | None = None,
    ) -> None:
        self.mapper = mapper or FieldMapper()
        self.transforms = transforms or {}
        for field, chain in self.transforms.items():
            if not isinstance(chain, list):
                raise ConfigError(
                    f"transforms['{field}'] должен быть списком трансформаций"
                )

    def apply(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Сначала маппинг ключей, затем трансформации по полям"""
        mapped = self.mapper.apply(rows)
        if not self.transforms:
            return mapped
        return [self._apply_row(row) for row in mapped]

    def _apply_row(self, row: dict[str, Any]) -> dict[str, Any]:
        new_row = dict(row)
        for field, chain in self.transforms.items():
            if field not in new_row:
                continue  
            value = new_row[field]
            for fn in chain:
                value = fn(value)
            new_row[field] = value
        return new_row
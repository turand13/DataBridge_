"""Базовые интерфейсы и ошибки для конвертеров данных"""
from abc import ABC, abstractmethod
from typing import Any


class ConfigError(Exception):
    """Понятная ошибка конфигурации конвертации"""


class TransformError(Exception):
    """Ошибка выполнения трансформации"""


class Transform(ABC):
    """Абстрактная трансформация одного значения

      - __call__(value) принимает любое значение, возвращает преобразованное
      - если тип значения не подходит — возвращает его БЕЗ ИЗМЕНЕНИЙ
      - None всегда проходит насквозь (отсутствие значения не трансформируем)
    """

    @abstractmethod
    def __call__(self, value: Any) -> Any:
        ...
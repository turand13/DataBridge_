"""Базовые интерфейсы и ошибки для всех Writer'ов"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataWriteError(Exception):
    """Понятная ошибка записи файла"""


class Writer(ABC):
    """Абстрактный интерфейс записи списка словарей в файл"""

    extensions: tuple[str, ...] = ()

    @abstractmethod
    def write(self, rows: list[dict[str, Any]], path: Path) -> None:
        """Записать данные в файл. Бросает DataWriteError при проблемах"""
        ...
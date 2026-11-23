"""Базовые интерфейсы и ошибки для всех Reader'ов"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class DataReadError(Exception):
    """Читаемая ошибка чтения файла"""


class Reader(ABC):
    """Абстрактный интерфейс чтения файла в список словарей"""
    # Расширения файлов, которые обрабатывает конкретный Reader.
    extensions: tuple[str, ...] = ()

    @abstractmethod
    def read(self, path: Path) -> list[dict[str, Any]]:
        """Прочитать файл и вернуть список записей"""
        ...
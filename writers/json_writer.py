"""Запись JSON-файлов"""
import json
from pathlib import Path
from typing import Any

from ._normalize import to_json_value
from .base import Writer, DataWriteError


class JsonWriter(Writer):
    """Writer для JSON"""

    extensions = (".json",)

    def __init__(self, indent: int = 2) -> None:
        self.indent = indent

    def write(self, rows: list[dict[str, Any]], path: Path) -> None:
        payload = [
            {k: to_json_value(v) for k, v in row.items()}
            for row in rows
        ]
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=self.indent)
        except OSError as e:
            raise DataWriteError(f"Не удалось записать {path.name}: {e}")
        except (TypeError, ValueError) as e:
            raise DataWriteError(f"Данные не сериализуются в JSON: {e}")
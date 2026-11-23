"""Чтение JSON-файлов"""
import json
from pathlib import Path
from typing import Any

from .base import Reader, DataReadError


class JsonReader(Reader):

    extensions = (".json",)

    def read(self, path: Path) -> list[dict[str, Any]]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise DataReadError(
                f"Битый JSON {path.name}: строка {e.lineno}, колонка {e.colno} — {e.msg}"
            )
        except UnicodeDecodeError:
            raise DataReadError(f"Файл {path.name} не в UTF-8. Проверьте кодировку.")

        if not isinstance(data, list):
            raise DataReadError(
                f"JSON {path.name}: ожидался массив объектов, получен {type(data).__name__}"
            )

        result: list[dict[str, Any]] = []
        for i, item in enumerate(data, start=1):
            if not isinstance(item, dict):
                raise DataReadError(
                    f"JSON {path.name}: элемент #{i} не объект, а {type(item).__name__}"
                )
            result.append({k: (v if v != "" else None) for k, v in item.items()})
        return result
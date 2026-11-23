"""Чтение XML-файлов"""
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from .base import Reader, DataReadError


class XmlReader(Reader):

    extensions = (".xml",)

    def read(self, path: Path) -> list[dict[str, Any]]:
        try:
            tree = ET.parse(path)
        except ET.ParseError as e:
            raise DataReadError(f"Битый XML {path.name}: {e}")
        except UnicodeDecodeError:
            raise DataReadError(f"Файл {path.name} не в UTF-8. Проверьте кодировку.")

        root = tree.getroot()
        records: list[dict[str, Any]] = []
        for i, child in enumerate(root, start=1):
            if len(child) == 0:
                raise DataReadError(
                    f"XML {path.name}: запись #{i} <{child.tag}> не содержит полей"
                )
            record: dict[str, Any] = {}
            for field in child:
                if len(field) > 0:
                    raise DataReadError(
                        f"XML {path.name}: запись #{i}, поле <{field.tag}> "
                        f"содержит вложенные теги — поддерживается только плоская структура"
                    )
                record[field.tag] = field.text if field.text not in ("", None) else None
            records.append(record)
        return records
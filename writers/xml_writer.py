"""Запись XML-файлов"""
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

from ._normalize import to_text
from .base import Writer, DataWriteError


class XmlWriter(Writer):
    """Writer для XML"""

    extensions = (".xml",)

    def __init__(self, root_tag: str = "records", record_tag: str = "record") -> None:
        self.root_tag = root_tag
        self.record_tag = record_tag

    def write(self, rows: list[dict[str, Any]], path: Path) -> None:
        root = ET.Element(self.root_tag)
        for row in rows:
            rec = ET.SubElement(root, self.record_tag)
            for key, value in row.items():
                field = ET.SubElement(rec, str(key))
                text = to_text(value)
                if text != "":
                    field.text = text
        tree = ET.ElementTree(root)
        try:
            ET.indent(tree, space="  ")
            tree.write(path, encoding="utf-8", xml_declaration=True)
        except OSError as e:
            raise DataWriteError(f"Не удалось записать {path.name}: {e}")
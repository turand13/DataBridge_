"""Нормализация значений для разных форматов записи"""
from datetime import date, datetime
from typing import Any


def to_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.isoformat()          
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")  
    return str(value)



def to_json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.strftime("%d.%m.%Y")
    return value

"""Генератор больших тестовых файлов для ручного тестирования и демо

Создаёт в samples/:
  large_valid.csv     — 1000 валидных записей
  large_invalid.csv   — 1000 записей, ~10% с ошибками
  large_valid.json    — те же 1000 валидных записей
  large_valid.xml     — те же 1000 валидных записей
  large_valid.xlsx    — те же 1000 валидных записей
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path
from xml.etree import ElementTree as ET

from openpyxl import Workbook


SAMPLES = Path(__file__).parent.parent / "samples"
N = 1000
INVALID_RATIO = 0.10  # ~10% записей с ошибками
SEED = 42             # фиксируем seed — данные воспроизводимы


FIRST_NAMES = ["Иван", "Мария", "Пётр", "Анна", "Олег", "Света", "Игорь", "Ольга",
               "Дмитрий", "Елена", "Сергей", "Татьяна", "Алексей", "Наталья"]
LAST_NAMES = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попов",
              "Васильев", "Соколов", "Михайлов", "Новиков"]
DOMAINS = ["mail.ru", "gmail.com", "yandex.ru", "example.com", "test.org"]


def make_valid_record(i: int) -> dict:
    """Сгенерировать одну валидную запись."""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    name = f"{first} {last}"
    email = f"user{i}@{random.choice(DOMAINS)}"
    age = random.randint(16, 100)
    birth = date(2024 - age, random.randint(1, 12), random.randint(1, 28))
    return {
        "id": i,
        "name": name,
        "email": email,
        "age": age,
        "birth_date": birth.strftime("%Y-%m-%d"),
    }


def make_invalid_record(i: int) -> dict:
    """Сгенерировать запись с одной случайной ошибкой (остальные поля — валидны)."""
    rec = make_valid_record(i)
    kind = random.choice([
        "bad_email", "bad_age", "empty_name", "bad_date", "dup_id", "age_low",
    ])
    if kind == "bad_email":
        rec["email"] = f"user{i}.mail.ru"           # без @
    elif kind == "bad_age":
        rec["age"] = random.choice([200, 150, 101]) # > max
    elif kind == "empty_name":
        rec["name"] = ""                            # пусто -> None при чтении CSV
    elif kind == "bad_date":
        rec["birth_date"] = "not-a-date"
    elif kind == "dup_id":
        rec["id"] = 1                               # дубликат с первой записью
    elif kind == "age_low":
        rec["age"] = random.randint(1, 15)          # < min
    return rec


# ---------- Writers ----------

def write_csv(rows: list[dict], path: Path) -> None:
    import csv
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_json(rows: list[dict], path: Path) -> None:
    path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def write_xml(rows: list[dict], path: Path) -> None:
    root = ET.Element("records")
    for row in rows:
        rec = ET.SubElement(root, "record")
        for key, value in row.items():
            field = ET.SubElement(rec, key)
            field.text = str(value) if value is not None else ""
    tree = ET.ElementTree(root)
    ET.indent(tree, space="  ")
    tree.write(path, encoding="utf-8", xml_declaration=True)


def write_xlsx(rows: list[dict], path: Path) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "data"
    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row.get(h) for h in headers])
    wb.save(path)
    wb.close()


# ---------- main ----------

def main() -> None:
    random.seed(SEED)
    SAMPLES.mkdir(exist_ok=True)

    valid = [make_valid_record(i) for i in range(1, N + 1)]

    # Невалидные: каждый INVALID_RATIO-й — с ошибкой, остальные — валидные.
    invalid: list[dict] = []
    n_invalid = int(N * INVALID_RATIO)
    invalid_indices = set(random.sample(range(N), n_invalid))
    for i in range(1, N + 1):
        if (i - 1) in invalid_indices:
            invalid.append(make_invalid_record(i))
        else:
            invalid.append(make_valid_record(i))

    write_csv(valid, SAMPLES / "large_valid.csv")
    write_csv(invalid, SAMPLES / "large_invalid.csv")
    write_json(valid, SAMPLES / "large_valid.json")
    write_xml(valid, SAMPLES / "large_valid.xml")
    write_xlsx(valid, SAMPLES / "large_valid.xlsx")

    print(f"valid:   {len(valid)} записей -> large_valid.{{csv,json,xml,xlsx}}")
    print(f"invalid: {len(invalid)} записей ({n_invalid} с ошибками) -> large_invalid.csv")


if __name__ == "__main__":
    main()
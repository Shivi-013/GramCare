import json
import os
from datetime import datetime
from typing import Any


def read_json(filepath: str) -> list:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_json(filepath: str, data: list) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_id(prefix: str, data: list) -> str:
    if not data:
        return f"{prefix}001"
    existing_ids = [int(item["id"][len(prefix):]) for item in data if item["id"].startswith(prefix)]
    next_num = max(existing_ids) + 1 if existing_ids else 1
    return f"{prefix}{str(next_num).zfill(3)}"


def get_by_id(data: list, item_id: str) -> dict | None:
    return next((item for item in data if item["id"] == item_id), None)


def delete_by_id(filepath: str, item_id: str) -> bool:
    data = read_json(filepath)
    original_len = len(data)
    data = [item for item in data if item["id"] != item_id]
    if len(data) < original_len:
        write_json(filepath, data)
        return True
    return False


def update_by_id(filepath: str, item_id: str, updates: dict) -> dict | None:
    data = read_json(filepath)
    for i, item in enumerate(data):
        if item["id"] == item_id:
            data[i].update(updates)
            data[i]["updated_at"] = datetime.now().isoformat()
            write_json(filepath, data)
            return data[i]
    return None


def now_iso() -> str:
    return datetime.now().isoformat()

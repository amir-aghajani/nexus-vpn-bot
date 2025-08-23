import json
from pathlib import Path
from typing import Any, Dict


class JSONStorage:
    def __init__(self, file_path: str = "storage.json"):
        self.file_path = Path(file_path)
        self._ensure_structure()

    def _ensure_structure(self):
        if not self.file_path.exists():
            self._save_data({
                "banned_users": [],
                "servers": [],
                "categories": [],
                "plans": [],
                "settings": {}
            })

    def _load_data(self) -> Dict[str, Any]:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self._ensure_structure()
            return {
                "banned_users": [],
                "servers": [],
                "categories": [],
                "plans": [],
                "settings": {}
            }

    def _save_data(self, data: Dict[str, Any]):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_component(self, component_name: str, default: Any = None) -> Any:
        data = self._load_data()
        return data.get(component_name, default)

    def set_component(self, component_name: str, value: Any):
        data = self._load_data()
        data[component_name] = value
        self._save_data(data)

    def update_component(self, component_name: str, updates: Dict[str, Any]):
        data = self._load_data()
        if component_name not in data:
            data[component_name] = {}
        if isinstance(data[component_name], dict):
            data[component_name].update(updates)
            self._save_data(data)
        else:
            raise ValueError(f"Component {component_name} is not a dictionary and cannot be updated")

    def add_to_list(self, component_name: str, item: Any):
        data = self._load_data()
        if component_name not in data:
            data[component_name] = []
        if isinstance(data[component_name], list):
            if item not in data[component_name]:
                data[component_name].append(item)
                self._save_data(data)
        else:
            raise ValueError(f"Component {component_name} is not a list")

    def remove_from_list(self, component_name: str, item: Any):
        data = self._load_data()
        if component_name in data and isinstance(data[component_name], list):
            if item in data[component_name]:
                data[component_name].remove(item)
                self._save_data(data)

    def is_in_list(self, component_name: str, item: Any) -> bool:
        data = self._load_data()
        component = data.get(component_name, [])
        return item in component if isinstance(component, list) else False


class UnifiedStorage:
    def __init__(self, file_path: str = "data/data.json"):
        self.storage = JSONStorage(file_path)

    def _ensure_list(self, component_name: str) -> list:
        data = self.storage.get_component(component_name, [])
        if not isinstance(data, list):
            data = []
            self.storage.set_component(component_name, data)
        return data

    def _find_index_by_id(self, items: list, identifier: Any, id_key: str) -> int:
        for i, it in enumerate(items):
            if isinstance(it, dict) and it.get(id_key) == identifier:
                return i
        return -1

    def _is_object_list(self, items: list) -> bool:
        return any(isinstance(it, dict) for it in items)

    def add(self, component_name: str, item_data: Any, id_key: str = "id", dedupe: bool = True):
        items = self._ensure_list(component_name)
        if isinstance(item_data, dict) and id_key in item_data and dedupe:
            idx = self._find_index_by_id(items, item_data[id_key], id_key)
            if idx >= 0:
                items[idx].update(item_data)
            else:
                items.append(item_data)
        else:
            if item_data not in items:
                items.append(item_data)
        self.storage.set_component(component_name, items)

    def remove(self, component_name: str, identifier: Any, id_key: str = "id") -> bool:
        items = self._ensure_list(component_name)
        if not items:
            return False
        if self._is_object_list(items) and identifier is not None:
            new_items = [it for it in items if not (isinstance(it, dict) and it.get(id_key) == identifier)]
            changed = len(new_items) < len(items)
            if changed:
                self.storage.set_component(component_name, new_items)
            return changed
        else:
            if identifier in items:
                items.remove(identifier)
                self.storage.set_component(component_name, items)
                return True
            return False

    def get(self, component_name: str, identifier: Any = None, id_key: str = "id"):
        data = self.storage.get_component(component_name, {} if component_name == "settings" else [])
        if identifier is None:
            return data
        if isinstance(data, dict):
            return data.get(identifier)
        if isinstance(data, list):
            if self._is_object_list(data):
                for it in data:
                    if isinstance(it, dict) and it.get(id_key) == identifier:
                        return it
                return None
            else:
                return identifier if identifier in data else None
        return None

    def update(self, component_name: str, identifier: Any, updates: Dict[str, Any], id_key: str = "id") -> bool:
        if component_name == "settings":
            self.storage.update_component("settings", {identifier: updates})
            return True
        items = self._ensure_list(component_name)
        if not items:
            return False
        if self._is_object_list(items):
            idx = self._find_index_by_id(items, identifier, id_key)
            if idx >= 0 and isinstance(items[idx], dict):
                items[idx].update(updates)
                self.storage.set_component(component_name, items)
                return True
            return False
        else:
            return False

    def set(self, component_name: str, data: Any):
        self.storage.set_component(component_name, data)

    def exists(self, component_name: str, identifier: Any, id_key: str = "id") -> bool:
        return self.get(component_name, identifier, id_key) is not None


def deep_json_load(obj):
    if isinstance(obj, dict):
        return {k: deep_json_load(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deep_json_load(i) for i in obj]
    elif isinstance(obj, str):
        try:
            return deep_json_load(json.loads(obj))
        except (json.JSONDecodeError, TypeError):
            return obj
    else:
        return obj


from datetime import datetime


def make_json_serializable(data):
    if isinstance(data, dict):
        return {k: make_json_serializable(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [make_json_serializable(v) for v in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif hasattr(data, "isoformat"):
        return data.isoformat()
    else:
        return data


server_status = {
    "enabled": "✅ فعال",
    "disabled": "❌ غیرفعال",
    "maintenance": "🔧 در حال نگهداری"
}

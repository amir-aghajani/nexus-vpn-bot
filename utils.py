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
    def __init__(self, file_path: str = "data.json"):
        self.storage = JSONStorage(file_path)

    def add(self, component_name: str, item_data: Any):
        self.storage.add_to_list(component_name, item_data)

    def remove(self, component_name: str, identifier: Any, id_key: str = "id"):
        current_data = self.storage.get_component(component_name, [])

        if not current_data:
            return False

        if isinstance(current_data, list):
            if len(current_data) > 0 and isinstance(current_data[0], dict):
                new_data = [item for item in current_data if item.get(id_key) != identifier]
                self.storage.set_component(component_name, new_data)
                return len(new_data) < len(current_data)
            else:
                # Simple list - remove value directly
                if identifier in current_data:
                    current_data.remove(identifier)
                    self.storage.set_component(component_name, current_data)
                    return True
        return False

    def get(self, component_name: str, identifier: Any = None, id_key: str = "id"):
        data = self.storage.get_component(component_name, [] if component_name != "settings" else {})

        if identifier is None:
            return data

        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            for item in data:
                if item.get(id_key) == identifier:
                    return item
            return None
        elif isinstance(data, dict):
            return data.get(identifier)
        else:
            return identifier if identifier in data else None

    def update(self, component_name: str, identifier: Any, updates: Dict[str, Any], id_key: str = "id"):
        if component_name == "settings":
            self.storage.update_component("settings", {identifier: updates})
            return True

        current_data = self.storage.get_component(component_name, [])

        if isinstance(current_data, list):
            for i, item in enumerate(current_data):
                if isinstance(item, dict) and item.get(id_key) == identifier:
                    current_data[i].update(updates)
                    self.storage.set_component(component_name, current_data)
                    return True
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


server_status = {
    "enabled": "✅ فعال",
    "disabled": "❌ غیرفعال",
    "maintenance": "🔧 در حال نگهداری"
}

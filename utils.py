import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


class JSONStorage:
    def __init__(self, file_path: str = "storage.json"):
        self.file_path = Path(file_path)
        self._ensure_structure()

    def _ensure_structure(self):
        if not self.file_path.exists():
            self._save_data({
                "banned_users": [],
                "servers": [],
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

    # Banned Users Methods
    def add_banned_user(self, user_id: int):
        self.storage.add_to_list("banned_users", user_id)

    def remove_banned_user(self, user_id: int):
        self.storage.remove_from_list("banned_users", user_id)

    def is_user_banned(self, user_id: int) -> bool:
        return self.storage.is_in_list("banned_users", user_id)

    def get_banned_users(self) -> List[int]:
        return self.storage.get_component("banned_users", [])
    
    def modify_user_status(self, user_id: int, action: str):
        if action == "banUser":
            self.add_banned_user(user_id)
        elif action == "unbanUser":
            self.remove_banned_user(user_id)
        else:
            raise ValueError(f"Unknown action: {action}")

    # Server Methods
    def add_server(self, server_data: Dict[str, Any]):
        servers = self.storage.get_component("servers", [])
        servers.append(server_data)
        self.storage.set_component("servers", servers)
        return

    def get_server(self, server_id: str) -> Optional[Dict[str, Any]]:
        servers = self.storage.get_component("servers", [])
        for server in servers:
            if server.get("id") == server_id:
                return server
        return None

    def update_server(self, server_id: str, updates: Dict[str, Any]):
        servers = self.storage.get_component("servers", [])
        for i, server in enumerate(servers):
            if server.get("id") == server_id:
                servers[i].update(updates)
                self.storage.set_component("servers", servers)
                return True
        return False

    def remove_server(self, server_id: str):
        servers = self.storage.get_component("servers", [])
        servers = [s for s in servers if s.get("id") != server_id]
        self.storage.set_component("servers", servers)

    def get_all_servers(self) -> List[Dict[str, Any]]:
        return self.storage.get_component("servers", [])

    # Settings Methods
    def set_setting(self, key: str, value: Any):
        self.storage.update_component("settings", {key: value})

    def get_setting(self, key: str, default: Any = None) -> Any:
        settings = self.storage.get_component("settings", {})
        return settings.get(key, default)

    def get_all_settings(self) -> Dict[str, Any]:
        return self.storage.get_component("settings", {})


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

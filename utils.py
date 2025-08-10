import json
from pathlib import Path


class BannedUsers:
    def __init__(self, file_path="banned_users.json"):
        self.file_path = Path(file_path)

    def load_banned_users(self):
        if not self.file_path.exists():
            return set()
        with open(self.file_path, "r", encoding="utf-8") as f:
            return set(json.load(f))

    def save_banned_users(self, banned_users):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(list(banned_users), f, indent=2)

    def modify_user_status(self, user_id: int, action: str):
        banned_users = self.load_banned_users()

        if action == "banUser":
            banned_users.add(user_id)
        elif action == "unbanUser":
            banned_users.discard(user_id)
        else:
            raise ValueError(f"Unknown action: {action}")

        self.save_banned_users(banned_users)

    def is_user_banned(self, user_id: int) -> bool:
        return user_id in self.load_banned_users()

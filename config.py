import os
import re
from typing import List

import dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings

dotenv.load_dotenv(dotenv_path=".env")


class Settings(BaseSettings):
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_bot_id: str = os.getenv("TELEGRAM_BOT_ID")
    telegram_bot_name: str = os.getenv("TELEGRAM_BOT_NAME")
    telegram_bot_admin_ids: List[int] = None
    firebase_admin_sdk: str = os.getenv("FIREBASE_ADMIN_SDK")

    @field_validator("telegram_bot_admin_ids", mode="before")
    def parse_admin_ids(cls, value: None) -> List[int]:
        admin_ids_str = os.getenv("TELEGRAM_BOT_ADMINS")
        try:
            admin_ids = [int(s) for s in re.findall(r'\d+', admin_ids_str)]
        except:
            admin_ids = []

        return admin_ids


settings = Settings()

from enum import Enum

from pydantic import BaseModel


class PanelTypes(str, Enum):
    sanaei = 'sanaei'
    marzban = 'marzban'


class StatusTypes(str, Enum):
    enabled = 'enabled'
    disabled = 'disabled'


class ServerCreateModel(BaseModel):
    name: str
    emoji: str
    configLimit: int = 250
    panelUrl: str
    panelUsername: str
    panelPassword: str
    panelType: PanelTypes
    status: StatusTypes

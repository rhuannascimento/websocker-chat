from enum import Enum
from typing import Optional
from pydantic import BaseModel


class MessageType(str, Enum):
    HANDSHAKE = "handshake"
    TEXT = "text"
    ERROR = "error"


class Message(BaseModel):
    type: MessageType
    sender_id: str
    content: str
    iv: Optional[str] = None
    tag: Optional[str] = None

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class RenderButton:
    text: str
    callback_data: str


@dataclass
class RenderMessage:
    text: str
    buttons: List[List[RenderButton]]
    image_bytes: Optional[bytes] = None

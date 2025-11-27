from dataclasses import dataclass
from typing import List


@dataclass
class TakeWith:
    items: List[str]

    def add(self, item: str):
        if item not in self.items:
            self.items.append(item)

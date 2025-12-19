from dataclasses import dataclass
from typing import List
from .clothing_item import ClothingItem


@dataclass
class Outfit:
    items: List[ClothingItem]

    def add(self, item: ClothingItem):
        if item not in self.items:
            self.items.append(item)

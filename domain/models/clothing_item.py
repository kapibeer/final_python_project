from enum import StrEnum
from dataclasses import dataclass
from typing import Optional, List


class ClothingCategory(StrEnum):
    OUTERWEAR = "outerwear"
    TOP = "top"
    BOTTOM = "bottom"


class ClothingSubtype(StrEnum):
    HOODIE = "hoodie"
    SWEATSHIRT = "sweatshirt"
    BLAZER = "blazer"
    SHIRT = "shirt"
    TSHIRT = "tshirt"

    JEANS = "jeans"
    TROUSERS = "trousers"
    SWEATPANTS = "sweatpants"

    COAT = "coat"
    JACKET = "jacket"
    OTHER = "other"


class Color(StrEnum):
    BLACK = "black"
    WHITE = "white"
    GREY = "grey"
    BEIGE = "beige"
    BROWN = "brown"
    BLUE = "blue"
    NAVY = "navy"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    PINK = "pink"
    PURPLE = "purple"


class Style(StrEnum):
    CASUAL = "casual"
    SPORT = "sport"
    CLASSIC = "classic"
    STREET = "street"
    BUSINESS = "business"
    PARTY = "party"
    HOME = "home"
    OUTDOOR = "outdoor"


class WarmthLevel(StrEnum):
    LIGHT = "light"
    MID = "mid"
    WARM = "warm"
    VERY_WARM = "very_warm"


class Length(StrEnum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


@dataclass
class ClothingItem:
    item_id: int
    owner_id: int
    image_id: str

    category: ClothingCategory
    subtype: ClothingSubtype

    main_color: Color
    secondary_color: Optional[Color]

    style: Style
    warmth_level: WarmthLevel
    length: Length

    is_waterproof: bool
    is_windproof: bool
    has_hood: bool

    embedding: List[float]

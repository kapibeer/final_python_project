from enum import StrEnum
from dataclasses import dataclass
from typing import Optional


class ClothingCategory(StrEnum):
    OUTERWEAR = "outerwear"
    TOP = "top"
    BOTTOM = "bottom"


class Color(StrEnum):
    BLACK = "black"
    WHITE = "white"
    GREY = "grey"
    BEIGE = "beige"
    BROWN = "brown"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    PINK = "pink"
    PURPLE = "purple"


class Style(StrEnum):
    CASUAL = "casual"
    SPORT = "sport"
    OFFICIAL = "official"
    EVENING = "evening" 


class WarmthLevel(StrEnum):
    LIGHT = "light"
    MEDIUM = "medium"
    WARM = "warm"


class OuterwearGroup(StrEnum):
    WINTER_OUTERWEAR = "winter_outerwear"
    DEMI_SEASON_OUTERWEAR = "demi_season_outerwear"
    LIGHT_OUTERWEAR = "light_outerwear"


class TopGroup(StrEnum):
    ONEPIECE_CLOTH = "onepiece_cloth"
    LAYERED_TOPS = "layered_tops"
    TRANSFORMABLE_TOPS = "transformable_tops"
    BASE_TOPS = "base_tops"
    KNITWEAR = "knitwear"


class BottomGroup(StrEnum):
    FULL_LENGTH_BOTTOMS = "full_length_bottoms"
    MID_LENGTH_BOTTOMS = "mid_length_bottoms"
    SHORT_LENGTH_BOTTOMS = "short_length_bottoms"


class ClothingSubtype(StrEnum):
    # Tops
    DRESS = "dress"
    ROMPER = "romper"
    JACKET = "jacket"
    ZIP-UP_HOODIE = "zip-up_hoodie"
    CARDIGAN = "cardigan"
    SHIRT = "shirt"
    TSHIRT = "tshirt"
    VEST = "vest"
    HOODIE = "hoodie"
    LONGSLEEVE = 'longsleeve'
    SWEATER = "sweater"

    # Bottoms
    JEANS = "jeans"
    TROUSERS = "trousers"
    SWEATPANTS = "sweatpants"
    SHORTS = "shorts"
    SKIRT = "skirt"
    CAPRIS = "capris"

    # Outerwear
    COAT = "coat"
    JACKET = "jacket"
    BOMBER = "bomber"
    TRENCH = "trench"
    PUFFER = "puffer"


@dataclass
class ClothingItem:
    item_id: int
    owner_id: int
    image_id: str

    main_color: Color

    style: Style = Style.CASUAL
    warmth_level: WarmthLevel = WarmthLevel.MEDIUM

    subtype: ClothingSubtype = ClothingSubtype.TSHIRT


@dataclass
class Outerwear(ClothingItem):
    group: OuterwearGroup = OuterwearGroup.LIGHT_OUTERWEAR
    is_waterproof: bool = False
    is_windproof: bool = False


@dataclass
class Top(ClothingItem):
    group: TopGroup = TopGroup.BASE_TOPS


@dataclass
class Bottom(ClothingItem):
    group: BottomGroup = BottomGroup.FULL_LENGTH_BOTTOMS

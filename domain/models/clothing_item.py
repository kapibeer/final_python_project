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
    NAVY = "navy"
    ORANGE = "orange"
    KHAKI = "khaki"
    MULTICOLOR = "multicolor"


class Style(StrEnum):
    CASUAL = "casual"
    SPORT = "sport"
    OFFICIAL = "official"
    PARTY = "party"
    STREET = "street"
    OUTDOOR = "outdoor"


class WarmthLevel(StrEnum):
    LIGHT = "light"
    MEDIUM = "medium"
    WARM = "warm"
    VERY_WARM = "very_warm"


class TopGroup(StrEnum):
    ONEPIECE_CLOTH = "onepiece_cloth"
    # цельные вещи
    LAYERED_TOPS = "layered_tops"
    # одежда, под которую нужно что-то поддевать (зипка, пиджак)
    TRANSFORMABLE_TOPS = "transformable_tops"
    # одежда, под которую можно что-то поддевать, а можно не поддевать
    BASE_TOPS = "base_tops"
    # базовый слой - одежда, которую поддевать (футболка, топ)
    FINAL_LAYER_TOPS = "final_layer_tops"
    # одежда, под которую ничего не подденешь (водолазка, боди)


class ClothingSubtype(StrEnum):
    # Onepiece cloth
    DRESS = "dress"                 # платье
    JUMPSUIT = "jumpsuit"           # кобменизон

    # Layered tops
    BLAZER = "blazer"               # пиджак
    ZIP_HOODIE = "zip_hoodie"       # зипка

    # Transformable tops
    HOODIE = "hoodie"               # худи
    LONGSLEEVE = 'longsleeve'       # лонгслив (любая кофта с длинным рукавом)
    CARDIGAN = "cardigan"           # кардиган
    SHIRT = "shirt"                 # рубашка

    # Final layer tops
    TURTLENECK = "turtleneck"       # водолазка
    BODYSUIT = "bodysuit"           # боди

    # Base tops
    TSHIRT = "tshirt"               # футболка
    TANK_TOP = "tank_top"           # майка, топик

    # Bottoms
    JEANS = "jeans"                 # джинсы
    TROUSERS = "trousers"           # брюки
    SWEATPANTS = "sweatpants"       # спортивные штаны/леггинсы
    SHORTS = "shorts"               # шорты
    SKIRT = "skirt"                 # юбки
    JOGGERS = "joggers"             # джоггеры

    # Outerwear
    COAT = "coat"                   # пальто
    JACKET = "jacket"               # куртка
    BOMBER = "bomber"               # бомбер
    TRENCH = "trench"               # тренч
    PUFFER = "puffer"               # пуховик
    FUR_COAT = "fur_coat"           # шуба
    SHEEPSKIN_COAT = "sheepskin_coat"  # дубленка
    WINDBREAKER = "windbreaker"     # ветровка
    JEANS_JACKET = "jeans_jacket"   # джинсовка
    BIKER_JACKET = "biker_jacket"   # косуха


SUBTYPE_TO_TOP_GROUP: dict[ClothingSubtype, TopGroup] = {
    # Onepiece cloth
    ClothingSubtype.DRESS: TopGroup.ONEPIECE_CLOTH,
    ClothingSubtype.JUMPSUIT: TopGroup.ONEPIECE_CLOTH,

    # Layered Tops
    ClothingSubtype.BLAZER: TopGroup.LAYERED_TOPS,
    ClothingSubtype.ZIP_HOODIE: TopGroup.LAYERED_TOPS,

    # Transformable Tops
    ClothingSubtype.HOODIE: TopGroup.TRANSFORMABLE_TOPS,
    ClothingSubtype.LONGSLEEVE: TopGroup.TRANSFORMABLE_TOPS,
    ClothingSubtype.CARDIGAN: TopGroup.TRANSFORMABLE_TOPS,
    ClothingSubtype.SHIRT: TopGroup.TRANSFORMABLE_TOPS,

    # Base Top
    ClothingSubtype.TSHIRT: TopGroup.BASE_TOPS,
    ClothingSubtype.TANK_TOP: TopGroup.BASE_TOPS,

    # Final Layer Tops
    ClothingSubtype.TURTLENECK: TopGroup.FINAL_LAYER_TOPS,
    ClothingSubtype.BODYSUIT: TopGroup.FINAL_LAYER_TOPS
}


@dataclass
class ClothingItem:
    item_id: int
    owner_id: int
    image_id: str

    category: ClothingCategory
    main_color: Color
    style: Style = Style.CASUAL
    warmth_level: WarmthLevel = WarmthLevel.MEDIUM
    subtype: ClothingSubtype = ClothingSubtype.TSHIRT

    is_waterproof: Optional[bool] = None
    is_windproof: Optional[bool] = None

    top_group: Optional[TopGroup] = None

    def __post_init__(self):
        self._determine_top_group()

    def _determine_top_group(self) -> None:
        if self.category == ClothingCategory.TOP:
            self.top_group = SUBTYPE_TO_TOP_GROUP.get(self.subtype)
        else:
            self.top_group = None

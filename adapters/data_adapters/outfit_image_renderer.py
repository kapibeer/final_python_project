from typing import List
from PIL import Image

from domain import Outfit


class OutfitImageRenderer:
    """
    Адаптер, который умеет собирать картинку аутфита.
    """

    def __init__(self) -> None:
        # сюда потом можно положить:
        # - доступ к хранилищу картинок
        # - настройки размеров
        # - сервис удаления фона и т.п.
        pass

    def render_outfit(self, outfit: Outfit) -> Image.Image:
        """
        Построить картинку аутфита по доменной модели.
        """
        width, height = 800, 800
        canvas = Image.new("RGB", (width, height), color="white")
        # TODO:
        # 1. по outfit.items достать картинки вещей
        # 2. убрать фон
        # 3. разложить на canvas
        return canvas

    def render_from_images(
        self,
        images: List[Image.Image],
        canvas_size: tuple[int, int] = (1000, 1000),
        bg_color: str | tuple[int, int, int] = "white",
    ) -> Image.Image:
        """
        Собрать картинку аутфита ТОЛЬКО по списку PIL.Image, без БД и домена.

        Использование:
            img = renderer.render_from_images([img1, img2, img3])
        """
        width, height = 800, 800
        canvas = Image.new("RGB", (width, height), color="white")
        return canvas

    def delete_background(self, image: Image.Image) -> Image.Image:
        """
        Удалить фон с картинки
        """
        width, height = 800, 800
        canvas = Image.new("RGB", (width, height), color="white")
        return canvas

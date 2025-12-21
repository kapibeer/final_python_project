from typing import List, Tuple, Callable, Awaitable, Optional
from PIL import Image
from domain.models.outfit import Outfit
from rembg import remove  # type: ignore
import io
from io import BytesIO


class OutfitImageRenderer:
    """
    Адаптер, который умеет собирать картинку аутфита.
    """

    def __init__(self) -> None:
        # сюда потом можно положить:
        # - доступ к хранилищу картинок
        # - настройки размеров
        # - сервис удаления фона и т.п.
        self.default_item_size = (350, 450)
        self.canvas_bg_color = (255, 255, 255)  # белый цвет фона
        pass

    async def render_outfit(
        self,
        outfit: Outfit,
        load_image: Callable[[str], Awaitable[Optional[Image.Image]]],
        canvas_size: Tuple[int, int] = (1000, 1000),
        layout: str = "grid",
    ) -> bytes:
        """
        Построить картинку аутфита по доменной модели.

        load_image(image_id) -> PIL.Image или None
        """
        images: List[Image.Image] = []

        for item in outfit.items:
            img = await load_image(item.image_id)
            if img is None:
                continue
            images.append(img)

        if not images:
            img = Image.new("RGB", canvas_size, color=self.canvas_bg_color)
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf.getvalue()

        img = self.render_from_images(
            images=images,
            canvas_size=canvas_size,
            bg_color=self.canvas_bg_color,
            layout=layout,
        )
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()

    def render_from_images(
        self,
        images: List[Image.Image],
        canvas_size: Tuple[int, int] = (1000, 1000),
        bg_color: str | Tuple[int, int, int] = "white",
        layout: str = "horizontal"
    ) -> Image.Image:
        """
        Собрать картинку аутфита ТОЛЬКО по списку PIL.Image.
        """
        if not images:
            return Image.new("RGB", canvas_size,
                             color=self._parse_color(bg_color))
        processed_images: list[Image.Image] = []
        for img in images:
            compressed_img = self._compress_image(img, self.default_item_size)
            clean_img = self.delete_background(compressed_img)
            processed_images.append(clean_img)

        bg_color_rgb = self._parse_color(bg_color)
        canvas = Image.new("RGB", canvas_size, color=bg_color_rgb)

        if layout == "grid":
            return self._layout_grid(canvas, processed_images)

        return canvas

    def delete_background(self, image: Image.Image) -> Image.Image:
        """
        Удаляет фон с изображения
        """
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        buf = io.BytesIO()
        image.save(buf, format="PNG")
        input_bytes = buf.getvalue()

        output_bytes: bytes = remove(input_bytes)  # type: ignore

        result = Image.open(io.BytesIO(output_bytes)).convert("RGBA")
        return result

    def _compress_image(self, image: Image.Image,
                        target_size: Tuple[int, int]) -> Image.Image:
        """
        Сжимает изображение до целевого размера с сохранением пропорций.
        """
        original_width, original_height = image.size
        target_width, target_height = target_size
        ratio = min(target_width / original_width,
                    target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        resized_image = image.resize((new_width, new_height),
                                     Image.Resampling.LANCZOS)
        return resized_image

    def _layout_grid(self, canvas: Image.Image, images: List[Image.Image],
                     cols: int = 2) -> Image.Image:
        """
        Расположить изображения в сетке.
        """
        canvas_width, canvas_height = canvas.size
        rows = (len(images) + cols - 1) // cols
        cell_width = self.default_item_size[0]
        cell_height = self.default_item_size[1]
        padding = 20
        grid_width = cols * cell_width + (cols - 1) * padding
        grid_height = rows * cell_height + (rows - 1) * padding
        start_x = max(0, (canvas_width - grid_width) // 2)
        start_y = max(0, (canvas_height - grid_height) // 2)
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            x = start_x + col * (cell_width + padding)
            y = start_y + row * (cell_height + padding)
            img_x = x + (cell_width - img.width) // 2
            img_y = y + (cell_height - img.height) // 2
            canvas.paste(img, (img_x, img_y), img)

        return canvas

    def _parse_color(self, color: str | Tuple[int, int, int]) \
            -> Tuple[int, int, int]:
        """
        Преобразовать цвет в формат RGB.
        """
        if isinstance(color, str):
            color_map = {
                'white': (255, 255, 255),
                'black': (0, 0, 0),
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'gray': (128, 128, 128),
                'grey': (128, 128, 128),
                'lightgray': (211, 211, 211),
                'lightgrey': (211, 211, 211),
            }
            return color_map.get(color.lower(), (255, 255, 255))
        return color

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO
from typing import List, Tuple, Callable, Awaitable, Optional

from PIL import Image
from rembg import remove, new_session  # type: ignore

from domain.models.outfit import Outfit


class OutfitImageRenderer:
    """
    Обработка фото
    """

    def __init__(
        self,
        max_workers: int = 2,
        default_item_size: Tuple[int, int] = (280, 360),
        canvas_bg_color: Tuple[int, int, int] = (255, 255, 255),
    ) -> None:
        self.default_item_size = default_item_size
        self.canvas_bg_color = canvas_bg_color

        self._session = new_session("u2net")
        self._pool = ThreadPoolExecutor(max_workers=max_workers)

    async def render_outfit(
        self,
        outfit: Outfit,
        load_image: Callable[[str], Awaitable[Optional[Image.Image]]],
        canvas_size: Tuple[int, int] = (800, 800),
        layout: str = "grid",
    ) -> bytes:
        coros = [load_image(item.image_id) for item in outfit.items]
        loaded = await asyncio.gather(*coros, return_exceptions=True)

        images: List[Image.Image] = []
        for x in loaded:
            if isinstance(x, Exception) or x is None:
                continue
            images.append(x)  # type: ignore

        if not images:
            return self._empty_png(canvas_size)

        canvas = Image.new("RGB", canvas_size, color=self.canvas_bg_color)
        if layout == "grid":
            canvas = self._layout_grid(canvas, images)

        buf = BytesIO()
        canvas.save(buf, format="PNG")
        return buf.getvalue()

    def _prepare_image_sync(self, img: Image.Image) -> Optional[Image.Image]:
        try:
            compressed = self._compress_image(img, self.default_item_size)
            cleaned = self._delete_background_sync(compressed)
            return cleaned
        except Exception:
            return None

    def _delete_background_sync(self, image: Image.Image) -> Image.Image:
        if image.mode != "RGBA":
            image = image.convert("RGBA")

        buf = BytesIO()
        image.save(buf, format="PNG")
        input_bytes = buf.getvalue()

        output_bytes: bytes = remove(input_bytes,  # type: ignore
                                     session=self._session)
        return Image.open(BytesIO(output_bytes)).convert("RGBA")

    async def delete_background(
        self,
        image_id: str,
        load_image: Callable[[str], Awaitable[Optional[Image.Image]]],
    ) -> tuple[bytes, bool]:
        try:
            img = await load_image(image_id)
        except Exception:
            return self._empty_png(self.default_item_size), False

        if img is None:
            return self._empty_png(self.default_item_size), False

        loop = asyncio.get_running_loop()
        processed = await loop.run_in_executor(
            self._pool,
            self._prepare_image_sync,
            img,
        )

        if processed is None:
            return self._empty_png(self.default_item_size), False

        buf = BytesIO()
        processed.save(buf, format="PNG")
        return buf.getvalue(), True

    # ---------- helpers ----------
    def _empty_png(self, canvas_size: Tuple[int, int]) -> bytes:
        img = Image.new("RGB", canvas_size, color=self.canvas_bg_color)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def _compress_image(self, image: Image.Image,
                        target_size: Tuple[int, int]) -> Image.Image:
        original_width, original_height = image.size
        target_width, target_height = target_size
        ratio = min(target_width / original_width,
                    target_height / original_height)
        new_width = max(1, int(original_width * ratio))
        new_height = max(1, int(original_height * ratio))
        return image.resize((new_width, new_height),
                            Image.Resampling.BILINEAR)

    def _layout_grid(self, canvas: Image.Image, images: List[Image.Image],
                     cols: int = 2) -> Image.Image:
        canvas_width, canvas_height = canvas.size
        rows = (len(images) + cols - 1) // cols
        cell_width, cell_height = self.default_item_size
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

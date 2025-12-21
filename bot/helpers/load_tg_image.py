from io import BytesIO
from PIL import Image
from aiogram import Bot


class LoaderTgImage:
    def __init__(self, bot: Bot | None):
        self.bot = bot

    async def load_tg_image(self, file_id: str) -> Image.Image | None:
        try:
            if self.bot is None:
                return None
            tg_file = await self.bot.get_file(file_id)
            stream = BytesIO()
            if tg_file.file_path is not None:
                await self.bot.download_file(tg_file.file_path,
                                             destination=stream)
                stream.seek(0)
                return Image.open(stream).convert("RGBA")
            return None
        except Exception:
            return None

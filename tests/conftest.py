# type: ignore
import sys
import types

# --- mock cv2 ---
cv2 = types.ModuleType("cv2")
cv2.dnn = types.ModuleType("cv2.dnn")
sys.modules["cv2"] = cv2
sys.modules["cv2.dnn"] = cv2.dnn

# --- mock rembg ---
rembg = types.ModuleType("rembg")


def fake_remove(*args, **kwargs):
    return b"", True


rembg.remove = fake_remove
sys.modules["rembg"] = rembg

# --- mock OutfitImageRenderer ---
fake_renderer = types.ModuleType("adapters.data_adapters"
                                 ".outfit_image_renderer")


class OutfitImageRenderer:
    async def delete_background(self, image_id, load_image):
        return b"fake", True

    async def render_outfit(self, outfit, load_image):
        return b"fake_png_bytes"


fake_renderer.OutfitImageRenderer = OutfitImageRenderer
sys.modules["adapters.data_adapters.outfit_image_renderer"] = fake_renderer

fake_container = types.ModuleType("infra.container")

fake_loader_mod = types.ModuleType("bot.helpers.load_tg_image")


class LoaderTgImage:
    def __init__(self, bot):
        self.bot = bot

    async def load_tg_image(self, image_id: str) -> bytes:
        return b"fake_image"


fake_loader_mod.LoaderTgImage = LoaderTgImage
sys.modules["bot.helpers.load_tg_image"] = fake_loader_mod


class Container:
    pass


fake_container.Container = Container
sys.modules["infra.container"] = fake_container

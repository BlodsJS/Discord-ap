import asyncio
from PIL import Image
from io import BytesIO
import discord
from discord import Member
from utils.handlers.dbs_handler import dbs_controller
import requests
from PIL import Image, ImageDraw
import discord
from discord import Member
from utils.handlers.dbs_handler import dbs_controller
from io import BytesIO
from easy_pil import load_image_async, Editor
import requests

class badges_controller:
    @staticmethod
    def _to_bytesio(image: Image.Image, filename: str) -> BytesIO:
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename=filename)

    @staticmethod
    async def get_member_avatar(member: Member):
        avatar_url = member.display_avatar.url
        response = await asyncio.to_thread(lambda: requests.get(avatar_url))
        avatar_bytes = BytesIO(response.content)
        avatar_img = await asyncio.to_thread(lambda: Image.open(avatar_bytes).convert("RGBA"))
        return avatar_img

    @staticmethod
    def make_circle(im: Image.Image, size: int = None) -> Image.Image:
        if size:
            im = im.resize((size, size), Image.LANCZOS)
        else:
            size = min(im.size)
            im = im.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(im, (0, 0), mask)
        return result

    @staticmethod
    async def badges_screen(member: Member):
        try:
            configs = dbs_controller.load_all_configs()
            img = Image.open(configs["profiles"]["badges_file"]).convert("RGBA")

            # Pegar avatar
            avatar = await badges_controller.get_member_avatar(member)
            avatar = badges_controller.make_circle(avatar, 255)
            img.paste(avatar, (200, 100), avatar)

            # Carregar badges do usuário
            user_profile = dbs_controller.load_profiles()
            user_badges = user_profile.get(str(member.id), {}).get("badges", [])

            size = (55, 55)
            start_x, start_y = 100, 410
            cols, step_x, step_y = 8, 74, 40

            # --- Carregar badges em paralelo ---
            async def load_badge_async(path):
                return await asyncio.to_thread(lambda: Image.open(path).convert("RGBA").resize(size))

            tasks = []
            positions = []
            for i, badge in enumerate(user_badges):
                badge_path = configs["badges"].get(badge, {}).get("file")
                if not badge_path:
                    continue
                tasks.append(load_badge_async(badge_path))
                positions.append((i % cols, i // cols))

            loaded_badges = await asyncio.gather(*tasks)

            # --- Colagem sequencial ---
            for badge_img, (col, row) in zip(loaded_badges, positions):
                x = start_x + col * step_x
                y = start_y + row * step_y
                img.paste(badge_img, (x, y), badge_img)

            return badges_controller._to_bytesio(img, f"badges_{member.name}.png")

        except Exception as e:
            print(f"Erro nas badges: {e}")

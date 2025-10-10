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
        response = requests.get(avatar_url)
        avatar_bytes = BytesIO(response.content)
        avatar_img = Image.open(avatar_bytes).convert("RGBA")
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
            avatar = await badges_controller.get_member_avatar(member)
            avatar = badges_controller.make_circle(avatar, 255)
            img.paste(avatar, (200, 100),avatar)
            user_profile = dbs_controller.load_profiles()
            flags = member.public_flags.all()
            user_badges = user_profile.get(str(member.id), {}).get("badges", [])
            flags = [str(flag).split(".")[-1] for flag in flags]
            flags.extend(user_badges)
            print(f"badges: {flags}")
            cols = 8   # número de colunas
            step_x = 74  # espaçamento horizontal
            step_y = 40  # espaçamento vertical
            start_x = 100
            start_y = 410
            size = (55, 55)  # tamanho de cada badge
            for i, badge in enumerate(user_badges):
                badge_path = configs["badges"].get(badge, {}).get("file")
                if not badge_path:
                    continue
                new_badge = Image.open(badge_path).convert("RGBA").resize(size)
                # posição na grade
                col = i % cols
                row = i // cols
                x = start_x + col * step_x
                y = start_y + row * step_y
                img.paste(new_badge, (x, y), new_badge)
            return badges_controller._to_bytesio(img, f"badges_{member.name}.png")
        except Exception as e:
            print(f"erro nas badges: {e}")
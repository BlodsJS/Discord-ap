from PIL import Image, ImageDraw
from io import BytesIO
import discord
from discord import Member
import requests
from utils.handlers.dbs_handler import dbs_controller
import asyncio
import time

class badges_controller:
    # Cache global das badges pré-carregadas e redimensionadas
    badge_cache = {}

    @staticmethod
    def _to_bytesio(image: Image.Image, filename: str) -> BytesIO:
        """Converte PIL Image para BytesIO, pronto para enviar ao Discord"""
        buffer = BytesIO()
        image.save(buffer, format="WEBP")
        buffer.seek(0)
        return discord.File(buffer, filename=filename)

    @staticmethod
    def make_circle(im: Image.Image, size: int) -> Image.Image:
        """Transforma a imagem em círculo, opcionalmente redimensionando"""
        im = im.resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size, size), fill=255)
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        result.paste(im, (0, 0), mask)
        return result

    @staticmethod
    async def get_member_avatar(member: Member, size: int = 255) -> Image.Image:
        """Baixa o avatar do usuário e transforma em círculo"""
        response = await asyncio.to_thread(lambda: requests.get(member.display_avatar.url))
        avatar_bytes = BytesIO(response.content)
        avatar = Image.open(avatar_bytes).convert("RGBA")
        avatar = badges_controller.make_circle(avatar, size)
        return avatar

    @classmethod
    def preload_badges(cls, configs: dict, size=(50, 50)):
        """Pré-carrega e redimensiona todas as badges, armazenando no cache"""
        for badge_name, badge_info in configs["badges"].items():
            path = badge_info.get("file")
            if path and badge_name not in cls.badge_cache:
                try:
                    img = Image.open(path).convert("RGBA").resize(size)
                    cls.badge_cache[badge_name] = img
                except Exception as e:
                    print(f"Erro ao carregar badge '{badge_name}': {e}")

    @classmethod
    async def badges_screen(cls, member: Member):
        """Gera a imagem de perfil com avatar e badges"""
        try:
            start = time.perf_counter()
            configs = dbs_controller.load_all_configs()
            img = Image.open(configs["profiles"]["badges_file"]).convert("RGBA")

            # Avatar
            avatar = await cls.get_member_avatar(member)
            img.paste(avatar, (200, 100), avatar)

            # Pré-carregar badges (uma chamada inicial é suficiente)
            cls.preload_badges(configs)
            t1 = time.perf_counter()
            # Carregar badges do usuário
            user_profile = dbs_controller.load_profiles()
            user_badges = user_profile.get(str(member.id), {}).get("badges", [])

            # Layout grid
            cols, step_x, step_y = 8, 80, 80
            start_x, start_y = 100, 410
            
            for i, badge in enumerate(user_badges):
                badge_img = cls.badge_cache.get(badge)
                if not badge_img:
                    continue
                col = i % cols
                row = i // cols
                x = start_x + col * step_x
                y = start_y + row * step_y
                img.paste(badge_img, (x, y), badge_img)
            t2 = time.perf_counter()
            
            file =  cls._to_bytesio(img, f"badges_{member.name}.png")
            t3 = time.perf_counter()
            print(f"carregamento: {t1 - start:.2f}s, colagem: {t2 - t1:.2f}s, buffer: {t3 - t2:.2f}")
            return file

        except Exception as e:
            print(f"Erro nas badges: {e}")

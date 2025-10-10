from PIL import Image, ImageDraw, ImageFont
import discord
from discord import Member
from utils.handlers.dbs_handler import dbs_controller
from io import BytesIO

class badges_controller:
    @staticmethod
    def _to_bytesio(image: Image.Image, filename: str) -> BytesIO:
        """Converte PIL Image para BytesIO"""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename=filename)
    
    @staticmethod
    def bagdes_screen(member: Member):
        configs = dbs_controller.load_all_configs()
        img = Image.open(configs["profiles"]["badges_file"])
        badges = []
        user_profile = dbs_controller.load_profiles("profiles")
        for badge in user_profile[str(member.id)]["badges"]:
            new_badge = Image.open(configs["badges"][badge]["file"])
            if new_badge:
                new_badge = new_badge.resize((20, 20))
                img.paste(new_badge, (40, 300), new_badge)
        file = badges_controller._to_bytesio(img, f"bagdes_{member.name}.png")
        
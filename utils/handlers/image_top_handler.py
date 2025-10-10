# utils/handlers
import logging
import textwrap
import discord
from io import BytesIO
from typing import Optional, Tuple
from discord import Member
from PIL import Image, ImageDraw, ImageFont 
from easy_pil import Editor, Canvas, Font, load_image_async
from utils.handlers.dbs_handler import dbs_controller
from pathlib import Path
import os
import textwrap
import bisect
import random

logger = logging.getLogger(__name__)

class top_image:
    assets = {
        'theme': Path('utils/assets/themes/'),
        'houses': {
            'Leonipards': Path('utils/assets/arms/leonipards.png'),
            'Synexa': Path('util/assets/arms/synexa.png'),
            'Corbusier': Path('utils/assets/arms/corbusier.png'),
            'Vildjharta': Path('utils/assets/arms/vildjharta.png'),
            'cidadao': Path('utils/assets/arms/cidadao.png'),
            'imperador': Path("utils/assets/arms/imperador.png")
        },
        'model': Path('utils/assets/bei_model.png')
    }
    fonts = {
        'name': Font.poppins(variant="bold", size=25),
        'body': Font.poppins(size=14),
        'desc': Font.poppins(variant="bold", size=10),
        'rank': Font.poppins(size=20),
        'title': Font.poppins(variant="bold", size= 35),
        'profile': Font.poppins(size=22)
    }
    @staticmethod
    def _load_asset(asset_type: str, name: str, user_id: str = "1828") -> Optional[Editor]:
        logger.info(f"entrou no carregamento de tipo: {asset_type}")
        profiles = dbs_controller.load_profiles()
        banners = dbs_controller.load_banners()
        user_profile = profiles.get(user_id, {})
        try:
            if asset_type == 'house':
                path = top_image.assets['houses'].get(name)
                if path:
                    logger.info("tentou carregar imagem de house")
                    
                    return Image.open(path)

            elif asset_type == "desc":
                desc = user_profile.get("desc", "Fala padrão ainda será escrita")
                return desc
                
            elif asset_type == 'theme':
                
                
                theme_profile = user_profile.get("theme", "theme.png")
                
                theme_path = top_image.assets['theme']
                logger.info("tentou carregar tema")
                logger.info(f"path: {theme_path}, theme: {theme_profile}, final: {theme_path}/{theme_profile}")
                final_path = Image.open(f"{theme_path}/{theme_profile}")
                return final_path
            elif asset_type == 'model':

                return Image.open(top_image.assets['model'])
            elif asset_type == "view":
                theme_path = top_image.assets['theme']
                banner_path = banners.get(name)
                
                final_path = Image.open(f"{theme_path}{banner_path}")
                return final_path
                
        except Exception as e:
            logger.error(f"Erro ao carregar asset {name}: {e}")
        return None
    
    @staticmethod
    def create_image():
        try:
            logger.info("entrou e iniciou a criação")
            img = Image.new("RGB", (800, 600),(0,0,0))
            house_img = top_image._load_asset("house", "Leonipards", "760217401215156224")
            model_img = top_image._load_asset("model", "model")
            theme_img = top_image._load_asset("theme", "theme")
            logger.info("carregou todas as imagens")
            model_img.resize((800, 600))
            theme_img.resize((800, 400))
            house_img.resize((40, 41))
            img.paste(theme_img, (0,160))
            img.paste(model_img, (0,0), model_img)
            img.paste(house_img, (380, 40),  house_img)
            return top_image._to_bytesio(img, "profile.png")
        except Exception as e:
            logger.info(e)
    
    @staticmethod
    def _to_bytesio(image: Image.Image, filename: str) -> BytesIO:
        """Converte PIL Image para BytesIO"""
        try:
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            return discord.File(buffer, filename=filename)
        except Exception as e:
            logger.info(f"erro em buffer: {e}")
        
        
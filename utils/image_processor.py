# utils/image_processor.py
import logging
import textwrap
import discord
from io import BytesIO
from typing import Optional, Tuple
from discord import Member
from PIL import Image
from easy_pil import Editor, Canvas, Font, load_image_async

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.assets = {
            'profile_bg': 'profile.png',
            'houses': {
                'Leonipards': 'leonipards.png',
                'Synexa': 'synexa.png',
                # ... outros assets
            }
        }
        
        self.fonts = {
            'title': Font.poppins(variant="bold", size=40),
            'body': Font.poppins(size=18),
            'rank': Font.poppins(size=24)
        }

    async def _load_asset(self, asset_type: str, name: str) -> Optional[Editor]:
        try:
            if asset_type == 'house':
                path = self.assets['houses'].get(name)
                if path:
                    return Editor(await load_image_async(path))
            elif asset_type == 'background':
                return Editor(await load_image_async(self.assets['profile_bg']))
        except Exception as e:
            logger.error(f"Erro ao carregar asset {name}: {e}")
        return None

    async def create_xp_card(self, user: Member, xp: int, level: int, rank: int) -> BytesIO:
        """Cria o cartão de progresso de XP com ranking"""
        try:
            # Configurações base
            WIDTH, HEIGHT = 500, 140
            avatar_size = (70, 70)
            progress_bar = (250, 18)

            # Carregar elementos
            bg = Canvas((WIDTH, HEIGHT), color="#131515")
            avatar = await load_image_async(user.display_avatar.url)
            
            # Processar imagem
            editor = Editor(bg)
            editor.paste(Editor(avatar).resize(avatar_size).circle_image(), (80, 35))
            
            # Textos
            editor.text((158, 40), user.name, color="white", font=self.fonts['title'])
            editor.text((170, 100), f"Level {level}", color="white", font=self.fonts['body'])
            
            # Barra de progresso
            xp_needed = (level ** 2) * 100
            progress = min((xp / xp_needed) * 100, 100)
            editor.rectangle((158, 70), width=progress_bar[0], height=progress_bar[1], radius=10, outline="black")
            editor.bar((163, 73), progress_bar[0] - 5, progress_bar[1] - 5, progress, fill="white", radius=8)
            
            # Rank
            editor.text((20, 45), f"#{rank}", color="white", font=self.fonts['rank'])
            
            return self._to_bytesio(editor.image, "xp_card.png")
            
        except Exception as e:
            logger.error(f"Erro ao gerar XP card: {e}")
            return self._error_image()

    async def create_profile_card(self, user: Member, xp: int, level: int, house: str) -> BytesIO:
        """Cria o cartão de perfil completo com elementos customizados"""
        try:
            # Configurações
            BG_SIZE = (800, 600)
            AVATAR_POS = (5, 0)
            HOUSE_POS = (650, 20)
            
            # Carregar assets
            bg = await self._load_asset('background', 'profile_bg')
            avatar = await load_image_async(user.display_avatar.url)
            house_icon = await self._load_asset('house', house)
            
            # Montagem
            bg.resize(BG_SIZE)
            bg.paste(Editor(avatar).resize((188, 188)).circle_image(), AVATAR_POS)
            
            if house_icon:
                bg.paste(house_icon.resize((110, 110)), HOUSE_POS)
            
            # Adicionar textos
            self._add_profile_texts(bg, user, xp, level, house)
            
            return self._to_bytesio(bg.image, "profile.png")
            
        except Exception as e:
            logger.error(f"Erro ao gerar profile card: {e}")
            return self._error_image()

    def _add_profile_texts(self, editor: Editor, user: Member, xp: int, level: int, house: str):
        """Adiciona textos complexos ao perfil"""
        # Configurações de layout
        layouts = {
            'stats': {
                'position': (200, 40),
                'lines': [
                    f"BKZ: 0",
                    f"XP: {xp}/{(level ** 2) * 100}",
                ],
                'font': self.fonts['body']
            },
            # ... outros elementos de texto
        }
        
        for element, config in layouts.items():
            x, y = config['position']
            for i, line in enumerate(config['lines']):
                editor.text(
                    position=(x, y + (i * 30)),
                    text=line,
                    color="black",
                    font=config['font']
                )

    async def create_leaderboard(self, users_data: list, guild_icon: Optional[str] = None) -> BytesIO:
        """Gera imagem do ranking de usuários"""
        try:
            CARD_HEIGHT = 100
            WIDTH = 580
            
            # Calcular altura total
            height = (len(users_data) * CARD_HEIGHT) + 50
            bg = Editor(Canvas((WIDTH, height), color="#131515"))
            
            # Adicionar cabeçalho
            if guild_icon:
                icon = Editor(await load_image_async(guild_icon)).resize((50, 50)).circle_image()
                bg.paste(icon, (WIDTH//2 - 25, 10))
                
            # Processar cada usuário
            for index, user_data in enumerate(users_data, start=1):
                await self._add_leaderboard_entry(bg, user_data, index, CARD_HEIGHT)
            
            return self._to_bytesio(bg.image, "leaderboard.png")
            
        except Exception as e:
            logger.error(f"Erro ao gerar leaderboard: {e}")
            return self._error_image()

    def _to_bytesio(self, image: Image.Image, filename: str) -> BytesIO:
        """Converte PIL Image para BytesIO"""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return discord.File(buffer, filename=filename)

    def _error_image(self) -> BytesIO:
        """Gera imagem de erro padrão"""
        bg = Canvas((800, 600), color="#131515")
        editor = Editor(bg)
        editor.text((300, 300), "Erro ao gerar imagem", color="white")
        return self._to_bytesio(editor.image, "error.png")

# Uso:
# processor = ImageProcessor()
# xp_card = await processor.create_xp_card(user, xp=150, level=5, rank=10)


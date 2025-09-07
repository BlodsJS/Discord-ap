# utils/image_processor.py
import logging
import textwrap
import discord
from io import BytesIO
from typing import Optional, Tuple
from discord import Member
from PIL import Image, ImageDraw, ImageFont 
from easy_pil import Editor, Canvas, Font, load_image_async
from utils.handlers.dbs_handler import dbs_controler
import os
import textwrap
import bisect
import random

from . import utilsPort

logger = logging.getLogger(__name__)
logger.info("Image carregado")

class ImageProcessor(utilsPort):

    async def _load_asset(self, asset_type: str, name: str, user_id: str = "1828") -> Optional[Editor]:
        print(asset_type, "load asset tipo")
        profiles = self.use.get_profile()
        banners = self.use.check_profiles()
        user_profile = profiles.get(user_id, {})
        try:
            if asset_type == 'house':
                path = self.assets['houses'].get(name)
                if path:
                    
                    return Editor(path)

            elif asset_type == "desc":
                desc = user_profile.get("desc", "Fala padrão ainda será escrita")
                return desc
                
            elif asset_type == 'background':
                
                
                theme_profile = user_profile.get("theme", "theme.png")
                #user_profile = profiles.get(user_id, "theme.png")
                theme_path = self.assets['theme']
                final_path = Editor(f"{theme_path}{theme_profile}")
                return final_path
            elif asset_type == 'model':

                return Editor(self.assets['model'])
            elif asset_type == "view":
                theme_path = self.assets['theme']
                banner_path = banners.get(name)
                final_path = Editor(f"{theme_path}{banner_path}")
                return final_path
                
        except Exception as e:
            logger.error(f"Erro ao carregar asset {name}: {e}")
        return None

    async def create_xp_card(self, user: Member, xp: int, level: int, rank: int) -> BytesIO:
        """Cria o cartão de progresso de XP com ranking"""
        try:
            # Configurações base
            if user is None:
                user = await self.bot.fetch_user(user)
            WIDTH, HEIGHT = 500, 140
            avatar_size = (70, 70)
            progress_bar = (250, 18)
            taxa = await self.use.obter_taxa(self.inicios, self.fins, self.valores, level)
            xp_needed = await self.use.xp_calc(level, taxa)
            
            # Carregar elementos
            bg = Canvas((WIDTH, HEIGHT), color="#131515")
            avatar = await load_image_async(user.display_avatar.url)
            
            # Processar imagem
            editor = Editor(bg)
            editor.paste(Editor(avatar).resize(avatar_size).circle_image(), (80, 35))
            
            # Textos
            editor.text((158, 40), user.display_name, color="white", font=self.fonts['name'])
            editor.text((170, 100), f"Level {level}", color="white", font=self.fonts['body'])
            editor.text((20, 45), f"#{rank}", color="white", font=self.fonts['rank'])
            editor.text((320, 98), f"{int(xp):,}/{xp_needed:,} XP", color="white", font=self.fonts["body"])
            
            # Barra de progresso
            progress = (xp / xp_needed) * 100
            print(progress)
            editor.rectangle((158, 70), width=progress_bar[0], height=progress_bar[1], radius=10, outline="black", stroke_width=3)
            editor.bar((163, 73), progress_bar[0] - 5, progress_bar[1] - 5, progress, fill="white", radius=10)
            
            return self._to_bytesio(editor.image, "xp_card.png")
            
        except Exception as e:
            
            logger.error(f"Erro ao gerar XP card: {e}")
            return self._error_image()
    
    async def get_house(self, user: Member) -> str:
        if user.id in self.users:
            return self.users[user.id]
        CASAS = {
            1378828845439778988: "Leonipards",
            1378828844479549521: "Corbusier",
            1378828847482667168: "Synexa",
            1378828846593347775: "Vildjharta"
        }
        
        role_ids = {role.id for role in user.roles}
        casa_ids = CASAS.keys()
        
        # 3. Encontra a primeira interseção (se existir)
        casa_encontrada = next((CASAS[role_id] for role_id in role_ids & casa_ids), "cidadao")
        return casa_encontrada
        
    async def create_profile_card(self, user: Member, xp: int, level: int, house: str, rank: int, money, rep) -> BytesIO:
        """Cria o cartão de perfil completo com elementos customizados"""
        try:
            # Configurações
            BG_SIZE = (800, 600)
            AVATAR_POS = (14, 14)
          
            taxa = await self.use.obter_taxa(self.inicios, self.fins, self.valores, level)
            texts = dbs_controler.load_mind("thoughts")
            
            words = self.text_break(random.choice(texts), 20)
            desc = await self._load_asset("desc", "teste", str(user.id))
            descs = self.text_break(desc, 31)
            
            # Carregar assets
            bg = await self._load_asset('background', 'theme', str(user.id))
            bg = bg.resize(BG_SIZE)
            draw = ImageDraw.Draw(bg.image)
          
            model_img = await self._load_asset('model', 'model')
            model_img = model_img.resize(BG_SIZE)
            
            avatar = await load_image_async(user.display_avatar.url)
            avatar = Editor(avatar).resize((150, 150)).circle_image()
            
            house_icon = await self._load_asset('house', house)
            
            
            # Montagem
            bg.paste(model_img, (0, 0))
            bg.paste(avatar, AVATAR_POS)
            
            #textos
            bg.text((170, 19), user.display_name, self.fonts["title"], "white")

            #largura, altura = self.fonts["title"].getsize(user.name_display)
            name_width = draw.textlength(user.display_name, font=self.fonts["title"]) \
                     if hasattr(draw, 'textlength') \
                     else draw.textsize(user.display_name, font=self.fonts["title"])[0]
            
            arms_pos = int(name_width) +180
            HOUSE_POS = (arms_pos, 13)
            level_width = draw.textlength(f"Nivel {level}", font=self.fonts["profile"]) \
                     if hasattr(draw, 'textlength') \
                     else draw.textsize(f"Nível {level}", font=self.fonts["profile"])[0]
            i = 1
            xp_size = 204 + level_width
            xp_need = await self.use.xp_calc(level, taxa)
            logger.info(f"teoricamente xp necessário: {xp_need}")
            bg.text((xp_size+5, 65), f"({int(xp):,}/{(level ** 2) * taxa + 100}xp)", self.fonts["body"], "white")
            for word in words:
                bg.text((304, 291 + (i*15)), word, self.fonts["body"], "black")
                i+=1
            i = 1
            for desc in descs:
                bg.text((30, 475 + (i*15)), desc, self.fonts["desc"], "white")
                i+=1
            
            if house_icon:
                bg.paste(house_icon.resize((40, 41)), HOUSE_POS)
            
            # Adicionar textos
            self._add_profile_texts(bg, user, xp, level, house, rank, taxa, money, rep)
            return self._to_bytesio(bg.image, "profile.png")
            
        except Exception as e:
            logger.error(f"Erro ao gerar profile card: {e}")
            return self._error_image()
          
    def text_break(self, text: str, w: int):
        wrapped_text = textwrap.wrap(text, width=w)
        texts = []
        for i, line in enumerate(wrapped_text):
            texts.append(line)
        return texts
       
    def _add_profile_texts(self, editor: Editor, user: Member, xp: int, level: int, house: str, rank: int, taxa: int, money:int, rep: int):
        """Adiciona textos complexos ao perfil"""
        # Configurações de layout
        house = house.capitalize()
        
        layouts = {
            'stats': {
                'position': (204, 65),
                'lines': [
                    f"Nível {level}",
                    f"BKZ: {money:,}",
                    f"{rep:,}"
                ],
                'font': self.fonts['profile'],
                'color': "white"
            }
            # ... outros elementos de texto
        }
        
        for element, config in layouts.items():
            x, y = config['position']
            for i, line in enumerate(config['lines']):
                editor.text(
                    position= (x, y+ (i * 35)),
                    text=line,
                    color=config['color'],
                    font=config['font']
                )

    async def _add_leaderboard_entry(self, bg, user_data, display_rank, visual_index, card_height, taxa, name, avatar):
        """Adiciona uma entrada no ranking à imagem."""
        try:
            WIDTH = 580
            HEADER_HEIGHT = 5  # Altura do cabeçalho
    
            # Calcular posição Y do card
            y = HEADER_HEIGHT + visual_index * card_height
    
            # Cor de fundo alternada para cada linha
            card_color = "#2C2F33" if visual_index % 2 == 0 else "#23272A"
            #bg.rectangle((158, 70), width=250, height=23, radius=10, outline="black", stroke_width=3)
            minutos= int(user_data[4]/60)
            required_xp = (user_data[2]**2)*taxa +100
            xp_needed = await self.use.xp_calc(user_data[2], taxa)
            logger.info(f"teoricamente xp necessário: {xp_needed}")
            if avatar: 
                avatar = Editor(await load_image_async(avatar))
                avatar.resize((80, 80)).circle_image()
                bg.paste(avatar.image, (80, y + 10))
    
            # Configurações de texto
            text_color = "#FFFFFF"
            font_size = 25
            x_start = 180 if avatar else 40
    
            # Número do ranking
            bg.text(
                (23, y + 27), 
                f"#{display_rank}", 
                font=Font.poppins(size=22, variant="bold"), 
                color=text_color
            )
    
            # Nome do usuário
            bg.text(
                (x_start, y + 16), 
                name, 
                font=Font.poppins(size=font_size-3, variant="bold"), 
                color=text_color
            )
    
            # Nível e XP
            level_info = f"Level: {user_data[2]}"
            bg.text(
                (x_start, y + 45), 
                level_info, 
                font=Font.poppins(size=font_size - 9, variant="bold"), 
                color="#C0C0C0"
            )
            xp_info = f"XP: {int(user_data[1]):,}/{required_xp:,}"
            bg.text(
                (x_start, y + 60), 
                xp_info, 
                font=Font.poppins(size=font_size - 9, variant="bold"), 
                color="#C0C0C0"
            )
            
            message_info = f"Chat: {user_data[3]:,}"
            bg.text(
                (x_start+ 220, y + 60), 
                message_info, 
                font=Font.poppins(size=font_size - 9, variant="bold"), 
                color="#C0C0C0"
            )
            voice_info = f"Call: {minutos:,}"
            bg.text(
                (x_start+ 220, y +45), 
                voice_info, 
                font=Font.poppins(size=font_size - 9, variant="bold"), 
                color="#C0C0C0"
            )
            
    
            # Barra de progresso
            progress_width = 360 #barra de xp
            progress = (user_data[1] / required_xp) * progress_width
            bg.rectangle((x_start, y + 82), width = progress_width, height = 5, fill = "#40444A", radius = 4)
            bg.rectangle((x_start,y + 82), width = progress, height = 5, fill = "#5865F2", radius = 4)
    
        except Exception as e:
            logger.error(f"Erro ao adicionar entrada no ranking: {e}")
            
    async def create_leaderboard(self, users_data: list, guild, offset, bot, guild_icon: Optional[str] = None) -> BytesIO:
        """Gera imagem do ranking de usuários"""
        print(users_data)
        try:
            CARD_HEIGHT = 100
            WIDTH = 580
            
            # Calcular altura total
            height = (len(users_data) * CARD_HEIGHT)+ 20
            bg = Editor(Canvas((WIDTH, height), color="#131515"))
            
            # Adicionar cabeçalho
            if guild_icon:
                icon = Editor(await load_image_async(guild_icon)).resize((50, 50)).circle_image()
                bg.paste(icon, (WIDTH//2 - 25, 10))
                
            # Processar cada usuário
            for visual_index, user_data in enumerate(users_data):
                display_rank = offset + visual_index + 1
                taxa = await self.use.obter_taxa(self.inicios, self.fins, self.valores, user_data[2])
                member = guild.get_member(int(user_data[0])) if guild else None
                if member is None:
                    member = await bot.fetch_user(int(user_data[0]))
                name = member.display_name
                if member.display_name:
                    name = member.display_name
                avatar = member.avatar.url
                await self._add_leaderboard_entry(bg, user_data, display_rank, visual_index, CARD_HEIGHT, taxa, name, avatar)
            
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

    async def profile_view(self, banner) -> BytesIO:
        BG_SIZE = (800, 600)
        AVATAR_POS = (14, 14)
        bg = await self._load_asset('view', banner, "2394")
        bg = bg.resize(BG_SIZE)
        return self._to_bytesio(bg.image, "profile.png")

# Uso:
# processor = ImageProcessor()
# xp_card = await processor.create_xp_card(user, xp=150, level=5, rank=10)


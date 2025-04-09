# utils/image_processor.py
import logging
import textwrap
import discord
from io import BytesIO
from typing import Optional, Tuple
from discord import Member
from PIL import Image
from easy_pil import Editor, Canvas, Font, load_image_async
import os
import textwrap

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        self.base_path = os.path.dirname(__file__)
        
        self.assets = {
            # Certifique-se de que o nome do arquivo esteja correto.
            # Se o arquivo de fundo não existir, você pode precisar criar ou ajustar o nome.
            'profile_bg': os.path.join(self.base_path,'profile.png'),
            'houses': {
                'Leonipards': os.path.join(self.base_path,'leonipards.png'),
                'Synexa': os.path.join(self.base_path, 'synexa.png'),
                'Corbusier': os.path.join(self.base_path, 'corbusier.png'),
                'Vildjharta': os.path.join(self.base_path, 'vildjharta.png'),
                'cidadao': os.path.join(self.base_path, 'cidadao.png'),
                'imperador': os.path.join(self.base_path,"imperador.png")
                
            }
        }
        self.fonts = {
            'name': Font.poppins(variant="bold", size=25),
            'body': Font.poppins(size=14),
            'rank': Font.poppins(size=20)
        }
        self.users = {
        	315244726569926666: "imperador"
        }
        self.bei_word = [
        	"teste"
        ]

    async def _load_asset(self, asset_type: str, name: str) -> Optional[Editor]:
        print(asset_type, "load asset tipo")
        try:
            if asset_type == 'house':
                path = self.assets['houses'].get(name)
                if path:
                    
                    return Editor(path)
            elif asset_type == 'background':
                
                return Editor(self.assets['profile_bg'])
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
            xp_needed = (level ** 2) * 100
            # Carregar elementos
            bg = Canvas((WIDTH, HEIGHT), color="#131515")
            avatar = await load_image_async(user.display_avatar.url)
            
            # Processar imagem
            editor = Editor(bg)
            editor.paste(Editor(avatar).resize(avatar_size).circle_image(), (80, 35))
            
            # Textos
            editor.text((158, 40), user.name, color="white", font=self.fonts['name'])
            editor.text((170, 100), f"Level {level}", color="white", font=self.fonts['body'])
            editor.text((20, 45), f"#{rank}", color="white", font=self.fonts['rank'])
            editor.text((320, 98), f"{xp:,}/{xp_needed:,} XP", color="white", font=self.fonts["body"])
            
            # Barra de progresso
            progress = (xp / xp_needed) * 100
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
        	1227357334905290764: "Leonipards",
        	1227357084543225939: "Corbusier",
        	1227359011624456313: "Synexa",
        	1227358673056043018: "Vildjharta"
        }
        
        role_ids = {role.id for role in user.roles}
        casa_ids = CASAS.keys()
        
        # 3. Encontra a primeira interseção (se existir)
        casa_encontrada = next((CASAS[role_id] for role_id in role_ids & casa_ids), "cidadao")
        return casa_encontrada
	    
    async def create_profile_card(self, user: Member, xp: int, level: int, house: str, rank: int) -> BytesIO:
        """Cria o cartão de perfil completo com elementos customizados"""
        try:
            # Configurações
            BG_SIZE = (800, 600)
            AVATAR_POS = (12, 3)
            HOUSE_POS = (650, 20)
            
            # Carregar assets
            bg = await self._load_asset('background', 'profile_bg')
            avatar = await load_image_async(user.display_avatar.url)
            house_icon = await self._load_asset('house', house)
            # Montagem
            bg.resize(BG_SIZE)
            bg.paste(Editor(avatar).resize((173, 173)).circle_image(), AVATAR_POS)
            
            if house_icon:
                bg.paste(house_icon.resize((110, 110)), HOUSE_POS)
            
            # Adicionar textos
            self._add_profile_texts(bg, user, xp, level, house, rank)
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
	   
    def _add_profile_texts(self, editor: Editor, user: Member, xp: int, level: int, house: str, rank: int):
        """Adiciona textos complexos ao perfil"""
        # Configurações de layout
        words = self.text_break("Isso é um teste para ver como o texto se ajusta dentro da caixa de fala.", 27)
        descs = self.text_break("Isso é um teste para ver como o texto se ajusta dentro da caixa de fala.", 31)
        house = house.capitalize()
        layouts = {
            'stats': {
                'position': (200, 45),
                'lines': [
                    user.name,
                    f"BKZ: 0",
                    f"XP: {xp}/{(level ** 2) * 100}",
                ],
                'font': self.fonts['body'],
                'color': "black"
            },
            'ranks': {
            'position': (420, 45),
            'lines': [
            	f"Rank: #{rank}",
            	f"Cargo: {house}",
            	"Reps: 9,999"
            ],
            'font': self.fonts['body'],
            'color': "black"
            },
            'word': {
            	'position': (60, 260),
            	'lines': words,
            	'font': self.fonts['body'],
            	'color': "black"
            },
            'desc': {
            	'position': (30, 495),
            	'lines':descs,
            	'font': Font.poppins(variant="bold", size=16),
            	'color': "white"
            }
            # ... outros elementos de texto
        }
        
        for element, config in layouts.items():
            x, y = config['position']
            for i, line in enumerate(config['lines']):
                editor.text(
                    position=(x, y + (i * 18)),
                    text=line,
                    color=config['color'],
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


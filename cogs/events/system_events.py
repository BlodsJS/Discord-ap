from . import BaseEventCog
import discord
from discord import Guild
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)
logger.info("Evento carregado")

class SystemEvents(BaseEventCog):
    
    @commands.Cog.listener()
    async def on_ready(self):
        #await self.c_db.create()
        await self.change_presence(activity=discord.Game(name="Inicializando..."))
    
    @commands.Cog.listener()
    async def on_disconnect(self):
        await self.c_db._salvar_dados()
        logger.info("Canais salvos")

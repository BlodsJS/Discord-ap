from . import BaseEventCog
from discord import Guild
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class SystemEvents(BaseEventCog):
    
    @commands.Cog.listener()
    async def on_ready(self):
    	#await self.c_db.create()
    	print(self.c_db.dados)
    
    @commands.Cog.listener()
    async def on_disconnect(self):
    	await self.c_db._salvar_dados()

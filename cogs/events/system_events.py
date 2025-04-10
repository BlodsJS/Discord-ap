from . import BaseEventCog
from discord import Guild
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class SystemEvents(BaseEventCog):
    
    @commands.Cog.listener()
    async def on_ready(self):
    	pass

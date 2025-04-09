from . import BaseEventCog
from discord import Guild
from discord.ext import commands

class SystemEvents(BaseEventCog):
    @commands.Cog.listener()
    async def on_ready(self):
        
        print("tudo ok, sistema de eventos")
        

   


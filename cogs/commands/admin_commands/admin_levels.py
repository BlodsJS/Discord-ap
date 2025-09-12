from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
from utils.views.config_view import ConfigView
from utils.handlers.dbs_handler import dbs_controler
import re
import logging

class admin_level_commands(BaseCommands):
    
    @commands.command(name="addxp", aliases=["add xp"])
    @commands.has_permissions(administrator=True)
    async def addxp_prefix(self, ctx, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        need = (user_data["level"]**2) * taxa + 100
        need -= user_data["xp"]
        levels = 0
        i = xp
        embed = await self.use.create(f"XP adicionado por: {ctx.author.name}", f"✅ {i} XP adicionados a {user.mention}")
        if need <= xp:
            
            while need <= xp:
                levels +=1
                xp -= need
                taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"]+levels)
                need = ((user_data["level"]+levels)**2) *taxa +100
            await self.db.increment_level(user_id, levels)
            await self.db.set_field("xp", user_id, xp)
            sucess = await self.use.check_role(user_data["level"]+levels, user)
            await ctx.send(embed=embed)
            return
        
        await  self.db.increment_xp(user_id, xp)
        await self.use.log_save(f"XP adicionado por: {ctx.author.name}, XP adicionados a {user.mention}, xp: {i}")
        await ctx.send(embed=embed)
        
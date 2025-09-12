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

class admin_economy_commands(BaseCommands):
    
    @commands.command(name="addmoney", aliases=["add money"])
    @commands.has_permissions(administrator=True)
    async def addmoney_prefix(self, ctx, user: Member, money: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        await self.db.update_field(user_id, 'money', money)
        embed = await self.use.create(f"BKZ adicionado por {ctx.author.mention}", f"{money:,} BKZ foram adicionados a {use.name}")
        await self.use.log_save(f"BKZ adicionado por {ctx.author.name}, BKZ foram adicionados a {use.name}, BKZ: {money:,}")
        await ctx.send(embed=embed)
      
from . import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
import re
import logging
import random


logger = logging.getLogger(__name__)
bkz = "<:BKZ_Coin:1379630938232721568>"
class EconomyCommands(BaseCommands):
    logger.info("Economy carregado")
    
  
    @commands.command(name="carteira", aliases=["money"])
    async def wallet_prefix(self, ctx, user: Member = None):
        name_command = "carteira"
        user = user or ctx.author
        user_id = str(user.id)
        user_data = await self.level_sys.get_data(user.id)
        
        embed = await self.use.create(f"Wallet de {user.mention}", f"Money:\n\n    {bkz} {user_data['money']:,}")
        
        await ctx.send(embed=embed)

    @commands.command(name="trabalhar", aliases=["work"])
    async def work_prefix(self, ctx):
        name_command = "work"
        
        if self.bot.timer_controller.is_on_cooldown(ctx.author.id, name_command):
            left_timer = self.bot.timer_controller.get_time_left(ctx.author.id, name_command)
            embed = await self.use.create("danger", f"Você ainda não pode usar esse comando, falta {left_timer//60} minutos")
            await ctx.send(embed=embed)
            return
        timers = self.db_controler.load_timers("timers")
        self.bot.timer_controller.set_cooldown(ctx.author.id, name_command, timers[name_command]["seconds"])
        
        user = ctx.author
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        money = random.randint(500, 3000)
        await self.db.increment_money(user_id, money)
        embed = await self.use.create("Recompensa pelo trabalho", f"{user.name} ganhou {bkz} {money} por ter trabalhado pelo império")
        await ctx.send(embed=embed)
        
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
    
    @commands.command(name="carteira", aliases=["money"])
    async def wallet_prefix(self, ctx, user: Union[Member, int] = None):
        name_command = "carteira"
        user = user or ctx.author
        if isinstance(user, Member):
            user_id = str(user.id)
        elif isinstance(user, int):
            user_id = str(user)
        
        user_data = await self.db.get_user_data(user_id)
        msg = (
            f"> Money:\n\n    {bkz} {user_data['money']:,}\n\n"
            f"> Bank:\n\n    {bkz} {user_data['bank']:,}"
        )
        embed = await self.use.create(f"Wallet de {user.mention}", msg)
        
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
        embed = await self.use.create("Recompensa pelo trabalho", f"{user.name} ganhou {bkz} {money:,} por ter trabalhado pelo império")
        await ctx.send(embed=embed)
  
    @commands.command(name="depositar", aliases=["dep"])
    async def dep_prefix(self, ctx, value: str):
        name_command = "dep"
        user_id = str(ctx.author.id)
        user_data = await self.db.get_user_data(user_id)
        
      
        if value.lower() == "all":
            value = user_data["money"]
            
        else:
            try:
                value = int(value)
                if value <= 0:
                    embed = await self.use.create("Erro", f"{ctx.author.mention}, o valor deve ser maior que 0.")
                    return await ctx.send(embed=embed)
                
                if value > user_data["money"]:
                    embed = await self.use.create("Erro ao depositar o dinheiro", f"{ctx.author.mention} você não pode depositar mais do que você tem!!")
                    await ctx.send(embed=embed)
                    return
            except ValueError:
                embed = await self.use.create("Erro ao depositar o dinheiro", f"{ctx.author.mention} você precisa digitar um valor válido ou all")
                await ctx.send(embed=embed)
                return
      
        result = await self.db.dep_money(user_id, value)
        embed = await self.use.create("Dinheiro depositado com sucesso!", f"{ctx.author.mention} depositou {bkz}{value:,}")
        await ctx.send(embed=embed)
    
    @commands.command(name="sacar", aliases=["withdraw", "with"])
    async def with_prefix(self, ctx, value: Union[str, int, float]):
        name_command = "with"
        user_id = str(ctx.author.id)
        user_data = await self.db.get_user_data(user_id)
        
        if value.lower() == "all":
            value = user_data["bank"]
            
        else:
            try:
                value = int(value)
                if value <= 0:
                    embed = await self.use.create("Erro", f"{ctx.author.mention}, o valor deve ser maior que 0.")
                    return await ctx.send(embed=embed)
                
                if value > user_data["bank"]:
                    embed = await self.use.create("Erro ao sacar o dinheiro", f"{ctx.author.mention} você não pode sacar mais do que você tem!!")
                    await ctx.send(embed=embed)
                    return
            except ValueError:
                embed = await self.use.create("Erro ao sacar o dinheiro", f"{ctx.author.mention} você precisa digitar um valor válido ou all")
                await ctx.send(embed=embed)
                return
      
        result = await self.db.with_money(user_id, value)
        embed = await self.use.create("Dinheiro sacado com sucesso!", f"{ctx.author.mention} sacou {bkz}{value:,}")
        await ctx.send(embed=embed)
        
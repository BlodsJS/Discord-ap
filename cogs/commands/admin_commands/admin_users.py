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

class admin_user_commands(BaseCommands):
    
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, user: Union[Member, int, str], reason: str = ""):
        
        if not user:
            
            embed = await self.use.create("Erro", "Mencione um usuário para banir! Exemplo: `!ban @usuário [motivo]`")
            await ctx.send(embed=embed)
            return

        if isinstance(user, discord.Member):
            target = user
            user_id = user.id
        
        elif isinstance(user, int) or (isinstance(user, str) and user.isdigit()):
            user_id = int(user)
            target = await self.bot.fetch_user(user_id)
        
        else:
            embed = await self.use.create("Erro", "❌ Formato inválido! Use: `!ban @usuário` ou `!ban 123456`")
            await ctx.send(embed=embed)
            return

        async for ban_entry in ctx.guild.bans():
            if ban_entry.user.id == user_id:
                embed = await self.use.create("Aviso", f"⚠️ <@{user_id}> já está banido!")
                await ctx.send(embed=embed)
                return
        
        await ctx.guild.ban(target, reason=reason)
        embed = await self.use.create("✅ Banido!", f"<@{user_id}> foi banido\nMotivo: {reason}")
        await self.use.log_save(f"{ctx.author.name} baniu um usuario, usuario banido {user_id}, razão: {reason}")
        await ctx.send(embed=embed)
from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
from utils.views.config_view import ConfigView
from utils.handlers.dbs_handler import dbs_controller
import re
import logging

class admin_user_commands(BaseCommands):
    
    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_prefix(self, ctx, target: typing.Union[discord.Member, str] = None):
         if not target:
             embed= await self.use.create(f"Erro: comando requisitado por {ctx.author.mention}", "⚠️ Especifique um usuário (`@usuário`) ou `all` para resetar todos.")
             await ctx.send(embed=embed)
             return
             
         if isinstance(target, Member):  # Resetar um usuário específico
             user_id = str(target.id)
             result = await self.db.reset_user(user_id)
             embed = await self.use.create(f"Membro resetado por {ctx.author.mention}", f"✅ {target.mention} foi resetado: {result}")
             await self.use.log_save(f"Membro resetado por {ctx.author.name}, {target.name} foi resetado: {result}")
             await ctx.send(embed=embed)
             
         elif target.lower() == "all":  # Resetar todos
             affected = await self.db.reset_xp()
             embed = await self.use.create(f"XP resetado por {ctx.author.mention}", f"✅ Todos os usuários foram resetados! ({affected} afetados)")
             await self.use.log_save(f"XP resetado por {ctx.author.name}, Todos os usuários foram resetados!")
             await ctx.send(embed=embed)
             
         else:
             embed= await self.use.create(f"Erro: comando requisitado por {ctx.author.mention}", "⚠️ Alvo inválido. Use `@usuário` ou `all`.")
             await ctx.send(embed=embed)

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
      
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_prefix(self, ctx, user_id: int = None):
        if not user_id:
            embed = await self.use.create("Erro:","❌ Forneça um **ID** válido. Exemplo: `!unban 123456789`")
            await ctx.send(embed=embed)
            return
        
        async for ban_entry in ctx.guild.bans():
            if ban_entry.user.id == user_id:
                await ctx.guild.unban(ban_entry.user)
                embed = await self.use.create("✅ Sucesso!", f"<@{user_id}> desbanido!")
                await self.use.log_save(f"{ctx.author.name} desbaniu um usuario, usuario desbanido: {user_id}")
                await ctx.send(embed=embed)
                return
        
        embed = await self.use.create("Erro:", "❌ Usuário não encontrado na lista de bans.")
        await ctx.send(embed=embed)
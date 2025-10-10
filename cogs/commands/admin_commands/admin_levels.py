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

class admin_level_commands(BaseCommands):
  
    @commands.command(name="update", aliases=["up"])
    @commands.has_permissions(administrator=True)
    async def update_prefix(self, ctx, user: Member, field: str, amount: int):
        if field not in ["xp", "level", "message", "voice", "money", "rep"]:
            embed = await self.use.create("Erro: field  não encontrado", f"{ctx.author.mention}, o field {field} não existe, use uma das opçōes abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
        try:
            user_id = str(user.id)
            user_data = await self.db.get_user_data(user_id)
            if field == "voice":
                amount = amount*60
            
            value = user_data[field] + amount
            await self.db.update_field(user_id, field, value)
            await self.use.log_save(f"{field} foi atualizado por {ctx.author.name}, {amount}{field} foi adicionado a {user.name}")
            embed = await self.use.create(f"{field} foi atualizado por {ctx.author.mention}", f"{amount} {field} foi adicionado a {user.name}")
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Erro: {e}")
          
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

    @commands.command(name="addlevel")
    @commands.has_permissions(administrator=True)
    async def addlevel_prefix(self, ctx, user: Member, level: int):
        user_id = str(user.id)
        await self.db.increment_level(user_id, level)
        embed = await self.use.create(f"Level adicionado por {ctx.author.mention}", f"✅ {level} level adicionados para {user.mention}")
        await self.use.log_save(f"Level adicionado por: {ctx.author.name}, para {user.name}, levels: {level}")
        await ctx.send(embed=embed)

    """remove system"""
  
    @commands.command(name="updateremove", aliases=["upr"])
    @commands.has_permissions(administrator=True)
    async def updater_prefix(self, ctx, user: Member, field: str, amount: int):
        if field not in ["xp", "level", "message", "voice", "money", "rep"]:
            embed = await self.use.create("Erro: field  não encontrado", f"{ctx.author.mention}, o field {field} não existe, use uma das opçōes abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        if field == "voice":
            amount = amount*60
        
        if amount > user_data[field]:
            value = 1
            if field == "voice":
                value = 60
            
        else:
            value = user_data[field] - amount
        await self.db.updater_field(user_id, field, value)
        embed = await self.use.create(f"{field} foi atualizado por {ctx.author.mention}", f"{amount} {field} foi removido de {user.name}")
        await self.use.log_save(f" {field} foi atualizado por {ctx.author.name}, {amount} {field} foi removido de {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="removexp")
    @commands.has_permissions(administrator=True)
    async def remove_xp_prefix(self, ctx, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = xp
        if user_data["xp"] < xp:
            xp = user_data["xp"] - user_data["xp"] +1
        await self.db.retirar_xp(user_id, xp)
        embed = await self.use.create(f"XP removido por {ctx.author.mention}", f"u2705 {i} XP removidos para {user.mention}")
        await self.use.log_save(f"XP removido por {ctx.author.name}, XP removidos para {user.name}, xp: {i}")
        await ctx.send(embed=embed)

    @commands.command(name="removelevel")
    @commands.has_permissions(administrator=True)
    async def remove_level_prefix(self, ctx, user: Member, level: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = level
        if user_data["level"] < level:
            level = user_data["level"] - user_data["level"]+1
        await self.db.retirar_level(user_id, level)
        embed = await self.use.create(f"Level removido por {ctx.author.mention}", f"u2705 {i} level removidos para {user.mention}")
        await self.use.log_save(f"Level removido por: {ctx.author.name}, level removido de {user.name}, levels: {i}")
        await ctx.send(embed=embed)
        
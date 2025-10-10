
from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, Role
import re
import logging

class admin_role_commands(BaseCommands):
    
    @commands.command(name="addrole", aliases=["addcargo", "add cargo", "add role"])
    @commands.has_permissions(administrator=True)
    async def add_role_prefix(self, ctx, user: Member, role: Union[discord.Role, int]):
        if isinstance(role, int):
            sucess = await self.use.add_role(user, role)
            embed = await self.use.create("Cargo adicionado", f"cargo adicionado a {user.name}")
            await ctx.send(embed=embed)
            return
        sucess = await user.add_roles(role)
        embed= await self.use.create("cargo adicionado", f"cargo adicionado a {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="romverole", aliases=["removecargo", "remove cargo", "remove role"])
    @commands.has_permissions(administrator=True)
    async def remove_role_prefix(self, ctx, user: Member, role: Union[discord.Role, int]):
        if isinstance(role, int):
            sucess = await self.use.remove_role(user, role)
            embed = await self.use.create("Cargo removido", f"cargo removido de {user.name}")
            await ctx.send(embed=embed)
            return
        
        sucess = await user.remove_roles(role)
        embed= await self.use.create("cargo removido", f"cargo removido de {user.name}")
        await ctx.send(embed=embed)
    
    @commands.command(name="limpar cargo", aliases=["limparcargo", "lc"])
    @commands.has_permissions(administrator=True)
    async def remove_all_role_prefix(self, ctx, role: Union[discord.Role, int]):
        if isinstance(role, int):
            role = await ctx.guild.get_role(role)
        if not isinstance(role, discord.Role):
            await ctx.send("❌ Cargo inválido ou não encontrado.")
            return

        message = ""
        acount = 0
        for member in role.members:
            sucess = await member.remove_roles(role)
            message += f"{member.mention}\n"
            acount +=1
        embed = await self.use.create("Cargo removido", f"cargo removido de {acount} usuarios\n\n{message}")
        await ctx.send(embed=embed)
        
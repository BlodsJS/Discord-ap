
from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, Role
import re
import logging

class admin_role_commands(BaseCommands):
    
    @commands.command(name="addrole", aliases=["ar", "add role"])
    @commands.has_permissions(administrator=True)
    async def add_role_prefix(self, ctx, member: Member, role: Union[int, Role]):
        if isinstance(role, int):
            embed = await self.use.create("teste de cogs", "adição de cargo (apenas confirmando visualmente)")
            await ctx.send(embed=embed)
        
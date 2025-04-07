from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands, Member

class AdminCommands(BaseCommands):
    @commands.command(name="addxp")
    @commands.has_permissions(administrator=True)
    async def addxp_prefix(self, ctx, user: Member, xp: int):
        await self.level_sys.add_xp(user.id, xp)
        await ctx.send(f"✅ {xp} XP adicionados para {user.mention}")

    @app_commands.command(name="addxp", description="Adiciona XP a um usuário")
    @app_commands.describe(user="Usuário", xp="Quantidade de XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp_slash(self, interaction, user: Member, xp: int):
        await self.level_sys.add_xp(user.id, xp)
        await interaction.response.send_message(...)


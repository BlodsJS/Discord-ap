from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands

class BasicCommands(BaseCommands):
    @commands.command(name="ping")
    async def ping_prefix(self, ctx):
        """Responde com a latência do bot (prefix)"""
        await ctx.send(f"🏓 Pong! {round(self.bot.latency* 1000)}ms")

    @app_commands.command(name="ping", description="Verifica a latência do bot")
    async def ping_slash(self, interaction):
        """Responde com a latência do bot (slash)"""
        await interaction.response.send_message(
            f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @commands.command(name="ajuda", aliases=["help"])
    async def help_prefix(self, ctx):
        pass
# Implementação similar para help

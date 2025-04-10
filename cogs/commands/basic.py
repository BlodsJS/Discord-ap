from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)

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
    async def help_prefix(self, ctx, text: str = None):
        if text == "adm":
        	ajuda_msg = (
        		"addlevel @user amount - a.\n"
	            "diga <mensagem> - O bot repete a mensagem.\n"
	            "ask <pergunta> - Faz uma pergunta a Bei Bei.\n"
	            "xp - Mostra seu XP.\n"
	            "perfil - Exibe seu perfil.\n"
	            "top - Mostra o ranking dos usuários.\n"
	            "avatar - Exibe seu avatar."
            )
        else:
        	
        embed= self.use.create("**Comandos Disponíveis:**", ajuda_msg)
        embed.set_footer(text=f"Requisitado por {ctx.author.mention}")
        await ctx.send(embed= embed)

# Implementação similar para help

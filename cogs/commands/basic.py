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

    @commands.command(name="ajuda", aliases=["help", "s", 'search'])
    async def help_prefix(self, ctx, text: str = "basic"):
        	
        embed= await self.use.create("**Comandos Disponíveis:**", self.ht.textos[text])
        embed.set_footer(text=f"Requisitado por {ctx.author.name}")
        await ctx.send(embed= embed)
        
    @app_commands.command(name="help", description="Exibe a lista de comandos")
    async def help_slash(self, interaction, text: str = "basic"):
    	embed= await self.use.create("**Comandos Disponíveis:**", self.ht.textos[text])
    	embed.set_footer(text=f"Requisitado por {interaction.user.name}")
        
    	await interaction.response.send_message(embed= embed)

# Implementação similar para help

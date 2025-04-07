from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands, Member

class ProfileCommands(BaseCommands):
    @commands.command(name="perfil")
    async def profile_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        # Lógica usando self.processor e self.level_sys

    @app_commands.command(name="perfil", description="Exibe o perfil de um usuário")
    @app_commands.describe(user="Usuário para ver o perfil")
    async def profile_slash(self, interaction, user: Member = None):
        user = user or interaction.user
        # Lógica similar

    @commands.command(name="rank")
    async def rank_prefix(self, ctx):
        user_data = await self.level_sys.get_data(ctx.author.id)
        image = await self.processor.create_xp_card(ctx.author, 80, 1, 8)
        await ctx.send(file=image)

    @app_commands.command(name="rank", description="Exibe seu ranking")
    async def rank_slash(self, interaction):
        pass
        # Implementação similar


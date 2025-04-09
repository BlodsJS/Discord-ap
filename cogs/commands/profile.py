from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands, Member

class ProfileCommands(BaseCommands):
    @commands.command(name="profile")
    async def profile_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        user_data = await self.level_sys.get_data(user.id)
        user_id = str(user.id)
        rank = await self.level_sys.get_rank(user_id)
        house = await self.processor.get_house(user)
        image = await self.processor.create_profile_card(user, user_data["xp"], user_data["level"], house, rank)
        await ctx.send(file=image)
        
    #barra
    @app_commands.command(name="profile", description="Exibe seu perfil")
    async def profile_slash(self, interaction, user: Member = None):
        
        user = user or interaction.user
        user_id = str(user.id)
        user_data = await self.level_sys.get_data(user.id)
        rank = await self.level_sys.get_rank(user_id)
        house = await self.processor.get_house(user)
        image = await self.processor.create_profile_card(user, user_data["xp"], user_data["level"], house, rank)
        await interaction.response.send_message(file=image)
        
    @commands.command(name="rank")
    async def rank_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        user_data = await self.level_sys.get_data(user.id)
        user_id = str(user.id)
        rank = await self.level_sys.get_rank(user_id)
        image = await self.processor.create_xp_card(user, user_data["xp"], user_data["level"], rank)
        await ctx.send(file=image)
    
    #barra
    @app_commands.command(name="rank", description="Exibe seu ranking")
    async def rank_slash(self, interaction, user: Member = None):
        user = user or interaction.user
        user_data = await self.level_sys.get_data(user.id)
        user_id = str(user.id)
        rank = await self.level_sys.get_rank(user_id)
        print(rank, "rank do usuario")
        image = await self.processor.create_xp_card(user, user_data["xp"], user_data["level"], rank)
        await interaction.response.send_message(file=image)
    
    @commands.command(name="top")
    async def top_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        embed = discord.Embed(
    		title=f"Top users do servidor:",
    		description="Ainda em desenvolvimento",
    		color=discord.Color.default()
        )
        embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
        
    #barra
    @app_commands.command(name="top", description="Exibe o top do servidor")
    async def top_slash(self, interaction, user: Member = None):
        
        user = user or interaction.user
        embed = discord.Embed(
    		title=f"Top users do servidor:",
    		description="Ainda em desenvolvimento",
    		color=discord.Color.default()
        )
        embed.set_footer(text=f"Requisitado por {interaction.user.name}", icon_url=interaction.user.avatar.url)
    	
        await interaction.response.send_message(embed=embed)
        
    @commands.command(name="stats")
    async def stats_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        user_data = await self.level_sys.get_data(user.id)
        next= (user_data["level"] ** 2) * 100
        minutes = int(user_data["voice"]/60)
        embed = discord.Embed(
    		title=f"Top users do servidor:",
    		description="Ainda em desenvolvimento",
    		color=discord.Color.default()
    	)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Stats", value= f"Mensagens:\n{user_data['message']} - Mensagens\n\nTempo em calls:\n{minutes} - Minutos")
        embed.add_field(name="Experiência", value=f"Level: {user_data['level']}\nPróximo level:\n {user_data['xp']}/{next}")
        embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
    	
        await ctx.send(embed=embed)
        
    #barra
    @app_commands.command(name="stats", description="Exibe seu ranking")
    async def stats_slash(self, interaction, user: Member = None):
        user = user or interaction.user
        user_data = await self.level_sys.get_data(user.id)
        next= (user_data["level"] ** 2) * 100
        minutes = int(user_data["voice"]/60)
        embed = discord.Embed(
    		title=f"Stats de {user.name}",
    		description="Ainda em desenvolvimento",
    		color=discord.Color.default()
    	)
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Stats", value= f"Mensagens:\n{user_data['message']} - Mensagens\n\nVoices:\n{minutes} - Minutes")
        embed.add_field(name="Experiência", value=f"Level: {user_data['level']}\nPróximo level:\n {user_data['xp']}/{next}")
        embed.set_footer(text=f"Requisitado por {interaction.user.name}", icon_url=interaction.user.avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
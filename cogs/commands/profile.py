from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands, Member
import logging

logger = logging.getLogger(__name__)

class ProfileCommands(BaseCommands):
    
    class TopPaginationView(discord.ui.View):
	    def __init__(self, db, processor, author, guild, timeout=60):
	        super().__init__(timeout=timeout)
	        self.db = db
	        self.processor = processor
	        self.author = author
	        self.guild = guild
	        self.current_offset = 0
	        self.current_page = 1
	
	    async def update_leaderboard(self, interaction, offset):
	        self.current_offset = offset
	        users = await self.db.top_users(offset)
	        image = await self.processor.create_leaderboard(users, self.guild, offset)
	        
	        # Atualiza os botões
	        self.previous_button.disabled = (offset <= 0)
	        
	        await interaction.response.edit_message(
	            attachments= [image],
	            view=self
	        )
	
	    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.blurple, disabled=True)
	    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button):
	        if interaction.user != self.author:
	            return await interaction.response.send_message("Apenas o autor pode usar esta paginação!", ephemeral=True)
	        
	        self.current_page -= 1
	        new_offset = max(0, self.current_offset - 5)
	        await self.update_leaderboard(interaction, new_offset)
	
	    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.blurple)
	    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
	        if interaction.user != self.author:
	            return await interaction.response.send_message("Apenas o autor pode usar esta paginação!", ephemeral=True)
	        
	        self.current_page += 1
	        await self.update_leaderboard(interaction, self.current_offset + 5)
	
	    async def on_timeout(self):
	        # Remove os botões após o timeout
	        for item in self.children:
	            item.disabled = True
	        await self.message.edit(view=self)
	
    @commands.command(name="top")
    async def top_prefix(self, ctx, text:str = ""):
	    """Comando de prefixo com paginação"""
	    
	    if text == "money":
	    	
	    	top_users = await self.db.top_users_field("money", 0)
	    	if top_users:
	    		msg = ""
	    		streak = 0
	    		for  i in top_users:
	    			streak += 1
	    			member = ctx.guild.get_member(int(i[0])) #animal
	    			msg += f"{streak}# {member.mention} : {i[1]} BKZ\n"
	    		embed = await self.use.create("Top users do servidor - Money", msg)
	    		embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
	    		await ctx.send(embed=embed)
	    		return
	    	
	    elif text == "rep":
	    	
	    	top_users = await self.db.top_users_field("rep", 0)
	    	if top_users:
	    		msg = ""
	    		streak = 0
	    		for i in top_users:
	    			streak  += 1
	    			member = ctx.guild.get_member(int(i[0])) #animal
	    			msg += f"{streak}# {member.mention} : {i[1]} reps\n"
	    		embed = await self.use.create("Top users do servidor - Rep", msg)
	    		embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
	    		await ctx.send(embed=embed)
	    		return
	    users = await self.db.top_users()
	    image = await self.processor.create_leaderboard(users, ctx.guild, 0)
	    
	    view = self.TopPaginationView(self.db, self.processor, ctx.author, ctx.guild)
	    view.message = await ctx.send(file=image, view=view)
	
    @app_commands.command(name="top", description="Exibe o top do servidor com paginação")
    async def top_slash(self, interaction: discord.Interaction):
	    """Comando de barra com paginação"""
	    users = await self.db.top_users()
	    image = await self.processor.create_leaderboard(users, interaction.guild, 0)
	    
	    view = self.TopPaginationView(self.db, self.processor, interaction.user, interaction.guild)
	    await interaction.response.send_message(file=image, view=view)
	    view.message = await interaction.original_response()
	    
    
    @commands.command(name="profile", aliases=["perfil"])
    async def profile_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        user_data = await self.level_sys.get_data(user.id)
        user_id = str(user.id)
        rank = await self.level_sys.get_rank(user_id)
        house = await self.processor.get_house(user)
        image = await self.processor.create_profile_card(user, user_data["xp"], user_data["level"], house, rank, user_data['money'], user_data['rep'])
        await ctx.send(file=image)
        
    #barra
    @app_commands.command(name="profile", description="Exibe seu perfil")
    async def profile_slash(self, interaction, user: Member = None):
        
        user = user or interaction.user
        user_id = str(user.id)
        user_data = await self.level_sys.get_data(user.id)
        rank = await self.level_sys.get_rank(user_id)
        house = await self.processor.get_house(user)
        image = await self.processor.create_profile_card(user, user_data["xp"], user_data["level"], house, rank, user_data['money'], user_data['rep'])
        await interaction.response.send_message(file=image)
        
    @commands.command(name="rank")
    async def rank_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        user_data = await self.level_sys.get_data(user.id)
        user_id = str(user.id)
        rank = await self.level_sys.get_rank(user_id)
        print(rank)
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
        
    
    
    @commands.command(name="teste")
    async def teste_prefix(self, ctx, text: str = ""):
    	user = ctx.author
    	user_id = str(user.id)
    	user_data = await self.db.get_user_data(user_id)
    	embed = await self.use.create("comando top (money e rep) em desenvolvimento:", f"money:\n  {user_data['money']}\nrep:\n  {user_data['rep']}")
    	await ctx.send(embed=embed)
    #barra
        
    @commands.command(name="stats")
    async def stats_prefix(self, ctx, user: Member = None):
        user = user or ctx.author
        user_data = await self.level_sys.get_data(user.id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        next= (user_data["level"] ** 2) * taxa +100
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
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        next= (user_data["level"] ** 2) * taxa +100
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
    
    
        
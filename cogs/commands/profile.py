from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands, Member
import logging
from typing import Union
logger = logging.getLogger(__name__)
logger.info("Profile carregado")

class ProfileCommands(BaseCommands):
    
    class TopPaginationView(discord.ui.View):
        def __init__(self, db, processor, author, guild, bot, timeout=60):
            super().__init__(timeout=timeout)
            self.db = db
            self.processor = processor
            self.author = author
            self.guild = guild
            self.current_offset = 0
            self.current_page = 1
            self.bot = bot
    
        async def update_leaderboard(self, interaction, offset):
            self.current_offset = offset
            users = await self.db.top_users(offset)
            image = await self.processor.create_leaderboard(users, self.guild, offset, self.bot)
            
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
        name_command = "top"
        
        if text == "money":
            
            top_users = await self.db.top_users_field("money", 0)
            logger.info(f"comando top, money: {top_users}")
            bkz = "<:BKZ_Coin:1379630938232721568>"
            if top_users:
                msg = ""
                streak = 0
                try:
                    for i in top_users:
                        streak +=1
                        member = ctx.guild.get_member(int(i[0]))
                        if member is None:
                            msg += f"{streak}# {i[0]} : {i[1]:,} {bkz}\n"
                        else:
                            msg += f"{streak}# {member.mention} : {i[1]:,} {bkz}\n"
                        
                except Exception as e:
                    logger.info(f"erro no top money: {e}")
                logger.info(msg)
                embed = await self.use.create("Top users do servidor - Money", msg)
                embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
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
        image = await self.processor.create_leaderboard(users, ctx.guild, 0, self.bot)
        
        view = self.TopPaginationView(self.db, self.processor, ctx.author, ctx.guild, self.bot)
        view.message = await ctx.send(file=image, view=view)
    
    @app_commands.command(name="top", description="Exibe o top do servidor com paginação")
    async def top_slash(self, interaction: discord.Interaction):
        """Comando de barra com paginação"""
        users = await self.db.top_users()
        image = await self.processor.create_leaderboard(users, interaction.guild, 0, self.bot)
        
        view = self.TopPaginationView(self.db, self.processor, interaction.user, interaction.guild, self.bot)
        await interaction.response.send_message(file=image, view=view)
        view.message = await interaction.original_response()
        
    
    @commands.command(name="profile", aliases=["perfil"])
    async def profile_prefix(self, ctx, user: Union[Member, int] = None):
        name_command = "profile"
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
        else:
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
        
    @commands.command(name="rank", aliases=["xp", "XP", "Xp"])
    async def rank_prefix(self, ctx, user: Union[Member, int] = None):
        name_command = "rank"
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
        else:
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
        
    #barra
        
    @commands.command(name="stats", aliases=["status"])
    async def stats_prefix(self, ctx, user: Union[Member, int] = None):
        name_command = "stats"
        if isinstance(user, int):
            user = await self.bot.fetch_user(user)
        else:
            user = user or ctx.author
        
        user_data = await self.level_sys.get_data(user.id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        next= (user_data["level"] ** 2) * taxa +100
        minutes = int(user_data["voice"]/60)
        embed = discord.Embed(
            title=f"status de {user.mention}",
            description=" ",
            color=discord.Color.default()
        )
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Stats", value= f"Mensagens:\n{user_data['message']} - Mensagens\n\nTempo em calls:\n{minutes} - Minutos")
        embed.add_field(name="Experiência", value=f"Level: {user_data['level']}\nPróximo level:\n {int(user_data['xp'])}/{int(next)}")
        embed.set_footer(text=f"Requisitado por {ctx.author.name}", icon_url=ctx.author.avatar.url)
        
        await ctx.send(embed=embed)
        
    #barra

    @commands.command(name="banners")
    async def banners_prefix(self, ctx, field: str = "", banner: str = None):
        name_command = "banners"
        banners = self.use.check_profiles()
        logger.info(banners)
        if field == "view":
            
            if banner.lower() not in banners["banners"]:
                embed = await self.use.create("❌ Erro", f"O {banner} Não existe! por favor selecione um da lista de b!banners", discord.Color.red())
                await ctx.send(embed=embed)
                return
            try:
                
                image = await self.processor.profile_view(banner.lower())
            except Exception as e:
                logger.info(f"erro na imagem: {e}")
            
            await ctx.send(file=image)
            return
        if field == "add":
            if banner not in banners["banners"]:
                embed = await self.use.create("❌ Erro", f"O {banner} Não existe! por favor selecione um da lista de b!banners")
                await ctx.send(embed=embed)
                return
        msg = ""
        for i in banners["banners"]:
            msg += f"{i.capitalize()}\n"
        embed = await self.use.create("Banners padrões disponiveis:", msg)
        await ctx.send(embed=embed)

    @commands.command(name="edit", aliases=["editar"])
    async def edit_prefix(self, ctx, field: str = None, *, value: str = None):
        name_command = "edit"
        if field:
            if field.lower() not in ["banner", "descricao", "descrição"]:
                embed = await self.use.create("❌ Erro", "Opção invalidda, para ver as opções use o comando ```b!edit```")
                await ctx.send(embed=embed)
                return
            
            fields = {
                "banner": "theme",
                "tema": "theme",
                "descricao": "desc",
                "descrição": "desc"
            }
            
            field = fields.get(field.lower())
            logger.info(field)
            if field == "theme":
                banners = self.use.check_profiles()
                value = banners.get(value)
                
                if value == None:
                    embeed = await self.use.create("⚠️", "Esse banner nao existe")
                    await ctx.send(embed=embed)
                
            sucess = self.use.edit_profile(str(ctx.author.id), field, value)
            
            embed = await self.use.create("Perfil atualizado", f"{field} foi alterado com sucesso", discord.Color.green())
            await ctx.send(embed=embed)
            return
          
        msg =(
          "1. Banner\n"
          "2. Descrição"
        )
        logger.info(f"field: {field}. descricao: {value}")
        embed = await self.use.create("**Edição de perfil**", msg)
        await ctx.send(embed=embed)
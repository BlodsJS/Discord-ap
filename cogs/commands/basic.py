from . import BaseCommands
import discord
from discord.ext import commands
from discord import app_commands, Member
from typing import Union
import logging
from easy_pil import load_image_async, Editor
import datetime

logger = logging.getLogger(__name__)
logger.info("Basic carregado")

class BasicCommands(BaseCommands):

    @commands.command(name="ping")
    async def ping_prefix(self, ctx):
        """Responde com a latência do bot (prefix)"""
        name_command = "ping"
        
        if self.bot.timer_controller.is_on_cooldown(ctx.author.id, name_command):
            left_timer = self.bot.timer_controller.get_time_left(ctx.author.id, name_command)
            embed = await self.use.create("danger", f"Você ainda não pode usar esse comando, falta {left_timer//60} minutos")
            await ctx.send(embed=embed)
            return
        
        timers = self.db_controler.load_timers("timers")
        self.bot.timer_controller.set_cooldown(ctx.author.id, name_command, timers[name_command]["seconds"])
        
        
        embed = await self.use.create("🏓 Pong!", f"{round(self.bot.latency* 1000)}ms")
        await ctx.send(embed=embed)

    @commands.command(name="rep")
    async def rep_prefix(self, ctx, user: Union[Member, int], *, message=None):
        name_command = "rep"
        if not user:
            embed = await self.use.create("⚠️", "Nenhum usuario especificado!")
            await ctx.send(embed=embed)
            return
        if isinstance(user, Member):
            target = user
        elif isinstance(user, int):
            user_id = int(user)
            target = await self.bot.fetch_user(user_id)
        else:
            embed = await self.use.create("⚠️", "Nenhum usuario especificado!")
            await ctx.send(embed=embed)
        
        user_id = str(target.id)
        cache_id = str(ctx.author.id)
        if user_id == cache_id:
            embed = await self.use.create("🚨", "Ora ora, vejo que alguém anda tentando explorar as brechas do império. Isso animou meu dia, uma tentativa hilária e lamentável.")
            await ctx.send(embed=embed)
            return
        if self.bot.timer_controller.is_on_cooldown(ctx.author.id, name_command):
            left_timer = self.bot.timer_controller.get_time_left(ctx.author.id, name_command)
            embed = await self.use.create("danger", f"Você ainda não pode usar esse comando, falta {left_timer//60} minutos")
            await ctx.send(embed=embed)
            return
        
        timers = self.db_controler.load_timers("timers")
        self.bot.timer_controller.set_cooldown(ctx.author.id, name_command, timers[name_command]["seconds"])

        user_data = await self.db.get_user_data(user_id)
        new = user_data['rep'] +1
        await self.db.update_field(user_id, 'rep', new)
        if not message:
            message = f"{target.display_name} foi abençoado após uma oração de {ctx.author.display_name}. Bei Bei seja louvada!"
        embed = await self.use.create("Reputação enviada com sucesso!", f"{ctx.author.mention} enviou uma rep a {user.mention}\nMensagem:\n> {message}")
        await ctx.send(embed=embed)

    @commands.command(name="ajuda", aliases=["help", "s", 'search'])
    async def help_prefix(self, ctx, field: str = ""):
        name_command = "ajuda"
        if field.lower() in ["basic", "admin", "profile", "house", "economy"]:
            embed = await self.use.create(f"Comandos de {field.upper()}", self.text.textos[field])
        else:
            msg = (
                "**basic** - Comandos básicos\n"
                "**admin** - Comandos administrativos\n"
                "**profile** - Comandos de perfil\n"
                "**house** - Comando das casas\n"
                "**economy** - Comandos de economia\n\n"
                "Use `help <categoria>` para ver os comandos específicos"
            )
            embed = await self.use.create("Sistema de Ajuda - Categorias Disponíveis", msg)

        embed.set_footer(text=f"Requisitado por {ctx.author.name}")
        await ctx.send(embed= embed)

    @commands.command(name="avatar")
    async def avatar_prefix(self, ctx, user: Union[Member, int]= None):
        name_command = "avatar"
        if user:
            if isinstance(user, int):
                user_id = int(user)
                user = await self.bot.fetch_user(user_id)
          
        user = user or ctx.author
        
        imagem = await load_image_async(user.display_avatar.url)
        editor = Editor(imagem).circle_image()
        file_img = discord.File(fp=editor.image_bytes, filename='circle.png')
        
        embed = await self.use.create(f"Avatar de {user.name}", " ")
        embed.set_image(url="attachment://circle.png")
        await ctx.send(file=file_img, embed=embed)

    @commands.command(name="diga", aliases= ["say"])
    async def say_prefix(self, ctx,*, text: str = ""):
        name_command = "diga"
        embed = await self.use.create("**Mensagem:**", text)
        embed.set_footer(text=f"By {ctx.author.name}")
        await ctx.send(embed=embed)

    @app_commands.command(name="diga", description="adiciona embed a uma mensagem")
    async def say_slash(self, interaction, text: str = ""):
        embed = await self.use.create("**Mensagem:**", text)
        embed.set_footer(text=f"By {interaction.user.name}")
        await interaction.response.send_message(embed= embed)
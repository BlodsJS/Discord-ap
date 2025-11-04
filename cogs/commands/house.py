from . import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
from utils.views.house_view import TestView
import re
import logging


logger = logging.getLogger(__name__)

class HouseCommands(BaseCommands):
    
    @commands.command(name="houses", aliases=["casas", "casa"])
    async def house_prefix(self, ctx, text: str = ""):
        user = ctx.author
        user_id = str(user.id)

        if not text:
            embed = await self.use.create("Sytema de Casas", "Em desenvolvimento. aqui estara as informações referentes as casas e o imperio.")
            await ctx.send(embed=embed)
            return
        
        elif text.lower() in ["leonipards", "corbusier", "synexa", "vildjharta"]:
            embed = await self.use.create(f"Casa {text}", "Em desenvolvimento, aqui estara as informações da casa, tais como seus membros, lideres, etc...")
            await ctx.send(embed=embed)
            return
        
        embed = await self.use.create("⚠️ Warning", "Essa casa não pertence ao império!!!")
        await ctx.send(embed=embed)
    
    @commands.command(name="history", aliases=["historia"])
    async def history_prefix(self, ctx, text: str = ""):
        user = ctx.author
        embed = await self.use.create("**Historia de bezirk!**", "Em desenvolvimento")
        await ctx.send(embed=embed)

    @commands.command(name="members")
    async def member_prefix(self, ctx, text: str = ""):
        user = ctx.author
        embed = await self.use.create(f"Membros da casa {text}", "em desenvolvimento")
        await ctx.send(embed=embed)


    @commands.command(name="houseticket", aliases=["htk"])
    async def teste_house_prefix(self, ctx, *, text: str = ""):
        user = ctx.author
        async def button_response(interact: discord.Interaction):
            houses = self.dbs_controler.load_house("houses")
            member = interact.guild.get_member(interact.user.id)
            for key, value in houses.items():
                if await self.use.has_role(member, value):
                    await interact.response.send_message(f"Você já tem uma casa: {interact.user.mention}", ephemeral=True)
                    return
            
            user_data = await self.db.get_user_data(str(interact.user.id))
            if user_data["level"] < houses["level_test"]:
                await interact.response.send_message(f"Você precisa ter no mínimo level {houses["level_test"]}: {interact.user.mention}", ephemeral=True)
                return
            
            user_thread = discord.utils.get(interact.channel.threads, name=f"Teste-{interact.user.name}")

            if user_thread:
                await interact.response.send_message(f"Você já tem uma thread: {user_thread.mention}", ephemeral=True)
                return
            
            thread = await interact.channel.create_thread(
                name=f"Teste-{interact.user.name}",
                type=discord.ChannelType.private_thread,  # Ou public_thread
                reason=f"Thread de teste para {interact.user.name}",
            )
            
            await thread.add_user(interact.user)
            await interact.response.send_message(f"Thread criada: {thread.mention}", ephemeral=True)
            thread_view = discord.ui.View()
            thread_botao = discord.ui.Button(
                label="Fechar teste",
                style = discord.ButtonStyle.red,
                custom_id= f"fechar_thread_{thread.id}"
            )
            thread_view.add_item(thread_botao)
            embed = await self.use.create(f"Teste de {interact.user.name}","Esta é sua área de testes privada!")
            await thread.send(embed=embed, view=thread_view)
            msg = ("Bem-vindo, se é que se pode usar essa palavra, ao jogo de **Casas** que o **Imperador** teceu para você."
                   " Um teatro, onde sua mediocridade será exposta, e sua lealdade, posta à prova.\n\n"
                   "Antes que dê o primeiro passo nessa jornada patética, saiba que a ignorância é uma escolha,"
                   "e você a escolhe com uma frequência perturbadora."
                   "Não há volta. **Não há segunda chance. Uma vez que uma resposta é enviada, ela é gravada na eternidade,"
                   "e todas as outras escolhas se fecham para sempre.**"
                   "Se a sua falta de jeito o levar a um resultado que não o agrada, não venha com lamúrias."
                   "O resultado, por mais que doa, é a verdade de sua alma insignificante, um reflexo preciso de sua natureza.\n\n"
                   "As Casas? Quatro pilares que sustentam o **Império Bezirk**."
                   "Quatro nomes que carregam o peso de eras."
                   "**Corbusier**, **Leonipards**, **Vildjharta** e **Synexa**."
                   "Apenas uma, no entanto, será digna de minha atenção."
                   "Escolha sabiamente... ou não. É mais divertido vê-lo cometer erros.")
            question_data = {
                "id":"q1",
                "text": msg
            }
            
            test_view = TestView(question_data, thread.id, user.id)
            embed = await self.use.create(
                "**Teste de inscrição à casa:**",
                question_data["text"]
            )
            await thread.send(embed=embed, view=test_view)
        
        
        try:
          view = discord.ui.View()
          botao = discord.ui.Button(label="Iniciar teste", style = discord.ButtonStyle.primary)
          botao.callback = button_response
          view.add_item(botao)
          embed = await self.use.create("**Teste para as Casas da Bezirk**", text)
          await ctx.send(embed=embed, view=view)
        except Exception as e:
            logger.info(f"erro no ticket: {e}")

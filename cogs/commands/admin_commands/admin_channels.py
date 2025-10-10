from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
import re
import logging

class admin_channel_commands(BaseCommands):
    @commands.command(name="addchannel", aliases=["ac", "add channel"])
    @commands.has_permissions(administrator=True)
    async def add_channel_prefix(self, ctx, canal: Union[TextChannel, VoiceChannel, discord.Thread]):
        if not isinstance(canal, (TextChannel, VoiceChannel, discord.Thread)):
            embed = await self.use.create("Erro:", f"❌ O canal {canal} não é válido. Use um canal de voz ou texto!")
            await ctx.send(embed=embed)
            return
        
        if isinstance(canal, VoiceChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "voice")
            if canal.id in canais:
                embed = await self.use.create("Erro:", "Esse canal já está adicionado")
                await ctx.send(embed=embed)
                return
            field = "voice"
        
        if isinstance(canal, TextChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "text")
            if canal.id in canais:
                embed = await self.use.create("Erro:", "Esse canal já está adicionado")
                await ctx.send(embed=embed)
                return
            field = "text"

        if isinstance(canal, discord.Thread):
            canais = self.c_db.get_canais(ctx.guild.id, "thread")
            if canal.id in canais:
                embed = await self.use.create("erro", "thread já está adicionado")
                await ctx.send(embed=embed)
                return
            field = "thread"
                
        sucess = await self.c_db.inserir(ctx.guild.id, canal.id, field)
        if sucess:
            
            embed = await self.use.create("Sucesso", f"Canal {canal} adicionado com sucesso a lista")
            # await self.use.arquivo(f"Canal {canal} adicionado com sucesso a lista por {ctx.name}")
            await ctx.send(embed=embed)
        else:
            embed = await self.use.create("Erro:", "não foi possível adicionar o canal")
            await ctx.send(embed=embed)
    
    @commands.command(name="removechannel", aliases=["rc"])
    @commands.has_permissions(administrator=True)
    async def remove_channel_prefix(self, ctx, canal: Union[TextChannel, VoiceChannel]):
        if not isinstance(canal, (TextChannel, VoiceChannel)):
            embed = await self.use.create("Erro:", f"{canal} não é um canal de voz ou texto vu00e1lido")
            await ctx.send(embed=embed)
            return
        
        if isinstance(canal, VoiceChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "voice")
            if not canal.id in canais:
                embed = await self.use.create("Erro:", "Esse canal não foi adicionado")
                await ctx.send(embed=embed)
                return
            field = "voice"
        
        if isinstance(canal, TextChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "text")
            if not canal.id in canais:
                logger.info(ctx)
                embed = await self.use.create("Erro:", "Esse canal não foi adicionado")
                await ctx.send(embed=embed)
                return
            field = "text"

        sucess = await self.c_db.apagar(ctx.guild.id, canal.id, field)
        if sucess:
            embed = await self.use.create("Sucesso", f"{canal} foi removido da lista")
            # await self.use.arquivo(f"Canal {canal} removido com sucesso da lista por {ctx.name}")
            await ctx.send(embed=embed)

    @commands.command(name="channel", aliases=["canais", "ch"])
    @commands.has_permissions(administrator=True)
    async def channel_prefix(self, ctx):
        canais = [f'<#{cid}>' for cid in self.c_db.get_canais(ctx.guild.id, "text")]
        v_canais = [f'<#{cid}>' for cid in self.c_db.get_canais(ctx.guild.id, "voice")]
        t_canais = [f'<#{cid}>' for cid in self.c_db.get_canais(ctx.guild.id, "thread")]
        text = ""
        voice =""
        thread = ""
        for i in canais:
            text += f"{i}\n"
            
        for i in v_canais:
            voice += f"{i}\n"

        for i in t_canais:
            thread+= f"{i}\n"
        
        embed = await self.use.create("Canais:", f"Canais de texto:\n{text}\n\nCanais de voz:\n{voice}\n\nTopicos:\n{thread}")
        await ctx.send(embed=embed)
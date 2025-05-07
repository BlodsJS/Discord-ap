from . import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
import re
import logging

logger = logging.getLogger(__name__)
logger.info("Admin carregado")

class AdminCommands(BaseCommands):

    @commands.command(name="addchannel", aliases=["ac", "add channel"])
    @commands.has_permissions(administrator=True)
    async def add_channel_prefix(self, ctx, canal: Union[TextChannel, VoiceChannel]):
        if not isinstance(canal, (TextChannel, VoiceChannel)):
            embed = await self.use.create("Erro:", f"{canal} nu00e3o u00e9 um canal de voz ou texto vu00e1lido")
            await ctx.send(embed=embed)
            return
        if isinstance(canal, VoiceChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "voice")
            if canal.id in canais:
                embed = await self.use.create("Erro:", "Esse canal ju00e1 estu00e1 adicionado")
                await ctx.send(embed=embed)
                return
                field = "voice"
        if isinstance(canal, TextChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "text")
            if canal.id in canais:
                embed = await self.use.create("Erro:", "Esse canal ju00e1 estu00e1 adicionado")
                await ctx.send(embed=embed)
                return
            field = "text"

        sucess = await self.c_db.inserir(ctx.guild.id, canal.id, field)
        if sucess:
            logger.info(ctx)
            embed = await self.use.create("Sucesso", f"Canal {canal} adicionado com sucesso a lista")
            # await self.use.arquivo(f"Canal {canal} adicionado com sucesso a lista por {ctx.name}")
            await ctx.send(embed=embed)
        else:
            embed = await self.use.create("Erro:", "Nu00e3o foi possu00edvel adicionar o canal")
            await ctx.send(embed=embed)

    @commands.command(name="removechannel", aliases=["rc"])
    @commands.has_permissions(administrator=True)
    async def remove_channel(self, ctx, canal: Union[TextChannel, VoiceChannel]):
        if not isinstance(canal, (TextChannel, VoiceChannel)):
            embed = await self.use.create("Erro:", f"{canal} nu00e3o u00e9 um canal de voz ou texto vu00e1lido")
            await ctx.send(embed=embed)
            return
        if isinstance(canal, VoiceChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "voice")
            if not canal.id in canais:
                embed = await self.use.create("Erro:", "Esse canal nu00e3o foi adicionado")
                await ctx.send(embed=embed)
                return
            field = "voice"
        if isinstance(canal, TextChannel):
            canais = self.c_db.get_canais(ctx.guild.id, "text")
            if not canal.id in canais:
                logger.info(ctx)
                embed = await self.use.create("Erro:", "Esse canal nu00e3o foi adicionado")
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
        print(canais)
        v_canais = [f'<#{cid}>' for cid in self.c_db.get_canais(ctx.guild.id, "voice")]
        text = ""
        voice =""
        for i in canais:
            text += f"{i}\n"
            
        for i in v_canais:
            voice += f"{i}\n"
        embed = await self.use.create("Canais:", f"Canais de texto:\n{text}\n\nCanais de voz:\n{voice}")
        await ctx.send(embed=embed)

    @commands.command(name="updateremove", aliases=["upr"])
    @commands.has_permissions(administrator=True)
    async def updater_prefix(self, ctx, user: Member, text: str, amount: int):
        if text not in ["xp", "level", "message", "voice", "money", "rep"]:
            embed = await self.use.create("Erro: field  não encontrado", f"{ctx.author.mention}, o field {text} não existe, use uma das opçōes abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
            embed = await self.use.create("Erro: field  nu00e3o encontrado", f"{ctx.author.mention}, o field {text} nu00e3o existe, use uma das opu00e7u014des abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        if text == "voice":
           amount = amount*60

        value = user_data[text] - amount
        if amount > user_data[text]:
            value = 1
        await self.db.updater_field(user_id, text, value)
        embed = await self.use.create(f"{text} foi atualizado por {ctx.author.mention}", f"{amount} foi removido de {user.name}")
        await ctx.send(embed=embed)
      
    @commands.command(name="update", aliases=["up"])
    @commands.has_permissions(administrator=True)
    async def update_prefix(self, ctx, user: Member, text: str, amount: int):
        if text not in ["xp", "level", "message", "voice", "money", "rep"]:
            embed = await self.use.create("Erro: field  não encontrado", f"{ctx.author.mention}, o field {text} não existe, use uma das opçōes abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)

        value = user_data[text] + amount
        await self.db.update_field(user_id, text, value)
        embed = await self.use.create(f"{text} foi atualizado por {ctx.author.mention}", f"{amount} foi adicionado a {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="addmoney", aliases=["add money"])
    @commands.has_permissions(administrator=True)
    async def addmoney_prefix(self, ctx, user: Member, money: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        await self.db.update_field(user_id, 'money', money)
        embed = await self.use.create("BKZ adicionado por {ctx.author.mention}", f"{money:,} BKZ foram adicionados a {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="addxp", aliases=["add xp"])
    @commands.has_permissions(administrator=True)
    async def addxp_prefix(self, ctx, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        need = (user_data["level"]**2) * taxa + 100
        need -= user_data["level"]
        levels = 0
        i = xp
        if need < xp:
            
            while need < xp:
                levels +=1
                xp -= need
                new = user_data["xp"] + levels
                taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, new)
                need = ((user_data["level"]+levels)**2) *taxa +100
            await self.db.increment_level(user_id, levels)
            
        await self.db.increment_xp(user_id, xp)
        embed = await self.use.create(f"XP adicionado por: {ctx.author.name}", f"✅ {i} XP adicionados para {user.mention}")
        logger.info(f"XP adicionado por: {ctx.author.name}, para {user.name}")
        await self.use.registrar_evento(f"XP adicionado por: {ctx.author.name}, para {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="addlevel")
    @commands.has_permissions(administrator=True)
    async def addlevel_prefix(self, ctx, user: Member, level: int):
        user_id = str(user.id)
        await self.db.increment_level(user_id, level)
        embed = await self.use.create(f"Level adicionado por {ctx.author.mention}", f"✅ {level} level adicionados para {user.mention}")
        logger.info(f"Level adicionado por: {ctx.author.name}, para {user.name} ")
        await self.use.registrar_evento(f"Level adicionado por: {ctx.author.name}, para {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="addrole", aliases=["addcargo", "add cargo"])
    @commands.has_permissions(administrator=True)
    async def addrole_prefix(self, ctx, user: Member, role: Union[discord.Role, int]):
        if isinstance(role, int):
            sucess = await self.use.add_role(user, role)
            embed = await self.use.create("Cargo adicionado", "provavelmente certo")

          
            await ctx.send(embed=embed)
            return
        sucess = await user.add_roles(role)
        embed= await self.use.create("cargo adicionado", "metodo tradicional")
        await ctx.send(embed=embed)
      
    @commands.command(name="removexp")
    @commands.has_permissions(administrator=True)
    async def removexp_prefix(self, ctx, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = xp
        if user_data["xp"] < xp:
            xp = user_data["xp"] - user_data["xp"] +1
        await self.db.retirar_xp(user_id, xp)
        embed = await self.use.create(f"XP removido por {ctx.author.mention}", f"u2705 {i} XP removidos para {user.mention}")
        logger.info(f"XP removido por: {ctx.author.name}, de {user.name} ")
        await ctx.send(embed=embed)

    @commands.command(name="removelevel")
    @commands.has_permissions(administrator=True)
    async def removelevel_prefix(self, ctx, user: Member, level: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = level
        if user_data["level"] < level:
            level = user_data["level"] - user_data["level"]+1
        await self.db.retirar_level(user_id, level)
        embed = await self.use.create(f"Level removido por {ctx.author.mention}", f"u2705 {i} level removidos para {user.mention}")
        logger.info(f"Level removido por: {ctx.author.name}, de {user.name} ")
        await ctx.send(embed=embed)

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_prefix(self, ctx, target: typing.Union[discord.Member, str] = None):
         if not target:
             embed= await self.use.create(f"Erro: comando requisitado por {ctx.author.mention}", "⚠️ Especifique um usuário (`@usuário`) ou `all` para resetar todos.")
             await ctx.send(embed=embed)
             return
             
         if isinstance(target, Member):  # Resetar um usuário específico
             user_id = str(target.id)
             result = await self.db.reset_user(user_id)
             embed = await self.use.create(f"Membro resetado por {ctx.author.mention}", f"✅ {target.mention} foi resetado: {result}")
             logger.info(f"Membro resetado por {ctx.author.name}, membro resetado: {target.name}")
             await ctx.send(embed=embed)
             
         elif target.lower() == "all":  # Resetar todos
             affected = await self.db.reset_xp()
             embed = await self.use.create(f"XP resetado por {ctx.author.mention}", f"✅ Todos os usuários foram resetados! ({affected} afetados)")
             logger.info(f"Todos os usuarios foram resetados por {ctx.author.name}")
             await ctx.send(embed=embed)
             
         else:
             embed= await self.use.create(f"Erro: comando requisitado por {ctx.author.mention}", "⚠️ Alvo inválido. Use `@usuário` ou `all`.")
             await ctx.send(embed=embed)
        
        
    #barras
    @app_commands.command(name="addxp", description="Adiciona XP a um usuário")
    @app_commands.describe(user="Usuário", xp="Quantidade de XP")
    
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp_slash(self, interaction, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        need = (user_data["level"]**2) * taxa + 100
        need -= user_data["level"]
        levels = 0
        i = xp
        if need < xp:
            
            while need < xp:
                levels +=1
                xp -= need
                new = user_data["xp"] + levels
                taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, new)
                need = ((user_data["level"]+levels)**2) *taxa +100
                
            print(levels)
            await self.db.increment_level(user_id, levels)
            
        await self.db.increment_xp(user_id, xp)
        embed = await self.use.create(f"XP adicionado por:{interaction.user.mention}", f"u2705 {i} XP adicionados para {user.mention}")
        logger.info(f"XP adicionado por:{
                    interaction.user.name}, para {user.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="addlevel", description="Adiciona level a um usuu00e1rio")
    @app_commands.describe(user="Usuu00e1rio", level="Quantidade de levels")
    @app_commands.checks.has_permissions(administrator=True)
    async def addlevel_slash(self, interaction, user: Member, level: int):
        user_id = str(user.id)

        await self.db.increment_level(user_id, level)
        embed = await self.use.create(f"Level adicionado por {interaction.user.mention}", f"u2705 {level} level adicionados para {user.mention}")
        logger.info(f"Level adicionado por:{
                    interaction.user.name}, para {user.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removexp", description="remove xp de um usuu00e1rio")
    @app_commands.describe(user="Usuu00e1rio", xp="Quantidade de xp")
    @app_commands.checks.has_permissions(administrator=True)
    async def removexp_slash(self, interaction, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = xp
        if user_data["xp"] > xp:
            xp = user_data["xp"] - user_data["xp"] +1
            
        await self.db.retirar_xp(user_id, xp)
        embed = await self.use.create(f"XP removido por{interaction.user.mention}", f"u2705 {i} XP removidos para {user.mention}")
        logger.info(f"XP removido por:{interaction.user.name}, de {user.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="removelevel", description="Adiciona level a um usuu00e1rio")
    @app_commands.describe(user="Usuu00e1rio", level="Quantidade de levels")
    @app_commands.checks.has_permissions(administrator=True)
    async def removelevel_slash(self, interaction, user: Member, level: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = level
        if user_data["level"] < level:
            level = user_data["level"] - user_data["level"] +1
            
        await self.db.retirar_level(user_id, level)
        embed = await self.use.create(f"Level removido por {interaction.user.mention}", f"u2705 {i} level removidos para {user.mention}")
        logger.info(f"Level removido por:{
                    interaction.user.name}, de {user.name}")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="reset", description="reseta um user ou todos")
    @app_commands.describe(target="alvo")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_slash(self, interaction, target: Member = None):
        if not target:
             embed= await self.use.create(f"Erro: comando requisitado por {interaction.user.mention}", "⚠️ Especifique um usuário (`@usuário`) ou `all` para resetar todos.")
             await interaction.response.send_message(embed=embed)
             return
            
        if target.lower() == "all":
            affected = await self.db.reset_xp()
            embed = await self.use.create(f"XP resetado por {interaction.user.mention}", f"✅ Todos os usuários foram resetados! ({affected} afetados)")
            logger.info(f"Todos os XP resetados por {interaction.user.name}")
            await interaction.response.send_message(embed=embed)
            return
        match = re.match(r'<@!?(\d+)>', target)
        if match:
            user_id = int(match.group(1))
            member = interaction.guild.get_member(user_id)
            if member:
                result = await self.db.reset_user(str(user_id))
                embed = await self.use.create(f"Membro resetado por {interaction.user.mention}", f"✅ {target.mention} foi resetado: {result}")
                logger.info(f"Membro resetado por {interaction.user.name}, membro resetado: {target.name}")
                await interaction.response.send_message(embed=embed)
                return
        else:
            embed= await self.use.create(f"Erro: comando requisitado por {interaction.user.mention}", "⚠️ Alvo inválido. Use `@usuário` ou `all`.")
            await interaction.response.send_message(embed=embed)
            return
            
    @commands.command(name="ban")
    @commands.has_permissions(administrator=True)
    async def ban_prefix(self, ctx, user: Member, reason: str = ""):
        embed = await self.use.create("Comando de ban", "Em desenvolvimento")

        await ctx.send(embed=embed)

    @app_commands.command(name="ban", description="Bane um usuario do servidor")
    @app_commands.describe(target="alvo")
    @app_commands.checks.has_permissions(administrator=True)
    async def ban_slash(self, interaction, target: Member, reason: str = ""):
        embed = await self.use.create("Comando de ban", "Em desenvolvimento")
        await interaction.response.send_message(embed=embed)

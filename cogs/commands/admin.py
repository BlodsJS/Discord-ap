from . import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
from utils.views.config_view import ConfigView
from utils.handlers.dbs_handler import dbs_controler
import re
import logging

logger = logging.getLogger(__name__)
logger.info("Admin carregado")

class AdminCommands(BaseCommands):
    
    """ _ _ _ _ _ _ _ _ _Channels methods _ _ _ _ _ _ _ _ _"""

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
    @commands.command(name="mas_mention", aliases=["msg all"])
    @commands.has_permissions(administrator=True)
    async def update_prefix(self, ctx,*, msg):
        embed = await self.use.create(" ", "Mensagem enviada para todos os membros do servidor")
        await ctx.send(embed=embed)
    """ _ _ _ _ _ _ _ _ _ User methods (level system) _ _ _ _ _ _ _ _ _"""

    """add system"""
          
    @commands.command(name="update", aliases=["up"])
    @commands.has_permissions(administrator=True)
    async def update_prefix(self, ctx, user: Member, field: str, amount: int):
        if field not in ["xp", "level", "message", "voice", "money", "rep"]:
            embed = await self.use.create("Erro: field  não encontrado", f"{ctx.author.mention}, o field {field} não existe, use uma das opçōes abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
        try:
            user_id = str(user.id)
            user_data = await self.db.get_user_data(user_id)
            if field == "voice":
                amount = amount*60
            
            value = user_data[field] + amount
            await self.db.update_field(user_id, field, value)
            await self.use.log_save(f"{field} foi atualizado por {ctx.author.name}, {amount}{field} foi adicionado a {user.name}")
            embed = await self.use.create(f"{field} foi atualizado por {ctx.author.mention}", f"{amount} {field} foi adicionado a {user.name}")
            await ctx.send(embed=embed)
        
        except Exception as e:
            logger.error(f"Erro: {e}")

    @commands.command(name="addxp", aliases=["add xp"])
    @commands.has_permissions(administrator=True)
    async def addxp_prefix(self, ctx, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        need = (user_data["level"]**2) * taxa + 100
        need -= user_data["xp"]
        levels = 0
        i = xp
        embed = await self.use.create(f"XP adicionado por: {ctx.author.name}", f"✅ {i} XP adicionados a {user.mention}")
        if need <= xp:
            
            while need <= xp:
                levels +=1
                xp -= need
                taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"]+levels)
                need = ((user_data["level"]+levels)**2) *taxa +100
            await self.db.increment_level(user_id, levels)
            await self.db.set_field("xp", user_id, xp)
            sucess = await self.use.check_role(user_data["level"]+levels, user)
            await ctx.send(embed=embed)
            return
        
        await  self.db.increment_xp(user_id, xp)
        await self.use.log_save(f"XP adicionado por: {ctx.author.name}, XP adicionados a {user.mention}, xp: {i}")
        await ctx.send(embed=embed)

    @commands.command(name="addlevel")
    @commands.has_permissions(administrator=True)
    async def addlevel_prefix(self, ctx, user: Member, level: int):
        user_id = str(user.id)
        await self.db.increment_level(user_id, level)
        embed = await self.use.create(f"Level adicionado por {ctx.author.mention}", f"✅ {level} level adicionados para {user.mention}")
        await self.use.log_save(f"Level adicionado por: {ctx.author.name}, para {user.name}, levels: {level}")
        await ctx.send(embed=embed)

    """remove system"""
  
    @commands.command(name="updateremove", aliases=["upr"])
    @commands.has_permissions(administrator=True)
    async def updater_prefix(self, ctx, user: Member, field: str, amount: int):
        if field not in ["xp", "level", "message", "voice", "money", "rep"]:
            embed = await self.use.create("Erro: field  não encontrado", f"{ctx.author.mention}, o field {field} não existe, use uma das opçōes abaixo:\n  xp, level, message, voice, money, rep")
            await ctx.send(embed=embed)
            return
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        if field == "voice":
            amount = amount*60
        
        if amount > user_data[field]:
            value = 1
            if field == "voice":
                value = 60
            
        else:
            value = user_data[field] - amount
        await self.db.updater_field(user_id, field, value)
        embed = await self.use.create(f"{field} foi atualizado por {ctx.author.mention}", f"{amount} {field} foi removido de {user.name}")
        await self.use.log_save(f" {field} foi atualizado por {ctx.author.name}, {amount} {field} foi removido de {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="removexp")
    @commands.has_permissions(administrator=True)
    async def remove_xp_prefix(self, ctx, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = xp
        if user_data["xp"] < xp:
            xp = user_data["xp"] - user_data["xp"] +1
        await self.db.retirar_xp(user_id, xp)
        embed = await self.use.create(f"XP removido por {ctx.author.mention}", f"u2705 {i} XP removidos para {user.mention}")
        await self.use.log_save(f"XP removido por {ctx.author.name}, XP removidos para {user.name}, xp: {i}")
        await ctx.send(embed=embed)

    @commands.command(name="removelevel")
    @commands.has_permissions(administrator=True)
    async def remove_level_prefix(self, ctx, user: Member, level: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = level
        if user_data["level"] < level:
            level = user_data["level"] - user_data["level"]+1
        await self.db.retirar_level(user_id, level)
        embed = await self.use.create(f"Level removido por {ctx.author.mention}", f"u2705 {i} level removidos para {user.mention}")
        await self.use.log_save(f"Level removido por: {ctx.author.name}, level removido de {user.name}, levels: {i}")
        await ctx.send(embed=embed)

    """danger system (resetes)"""

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
             await self.use.log_save(f"Membro resetado por {ctx.author.name}, {target.name} foi resetado: {result}")
             await ctx.send(embed=embed)
             
         elif target.lower() == "all":  # Resetar todos
             affected = await self.db.reset_xp()
             embed = await self.use.create(f"XP resetado por {ctx.author.mention}", f"✅ Todos os usuários foram resetados! ({affected} afetados)")
             await self.use.log_save(f"XP resetado por {ctx.author.name}, Todos os usuários foram resetados!")
             await ctx.send(embed=embed)
             
         else:
             embed= await self.use.create(f"Erro: comando requisitado por {ctx.author.mention}", "⚠️ Alvo inválido. Use `@usuário` ou `all`.")
             await ctx.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_prefix(self, ctx, user: Union[Member, int, str], reason: str = ""):
        
        if not user:
            
            embed = await self.use.create("Erro", "Mencione um usuário para banir! Exemplo: `!ban @usuário [motivo]`")
            await ctx.send(embed=embed)
            return

        if isinstance(user, discord.Member):
            target = user
            user_id = user.id
        
        elif isinstance(user, int) or (isinstance(user, str) and user.isdigit()):
            user_id = int(user)
            target = await self.bot.fetch_user(user_id)
        
        else:
            embed = await self.use.create("Erro", "❌ Formato inválido! Use: `!ban @usuário` ou `!ban 123456`")
            await ctx.send(embed=embed)
            return

        async for ban_entry in ctx.guild.bans():
            if ban_entry.user.id == user_id:
                embed = await self.use.create("Aviso", f"⚠️ <@{user_id}> já está banido!")
                await ctx.send(embed=embed)
                return
        
        await ctx.guild.ban(target, reason=reason)
        embed = await self.use.create("✅ Banido!", f"<@{user_id}> foi banido\nMotivo: {reason}")
        await self.use.log_save(f"{ctx.author.name} baniu um usuario, usuario banido {user_id}, razão: {reason}")
        await ctx.send(embed=embed)
      
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_prefix(self, ctx, user_id: int = None):
        if not user_id:
            embed = await self.use.create("Erro:","❌ Forneça um **ID** válido. Exemplo: `!unban 123456789`")
            await ctx.send(embed=embed)
            return
        
        async for ban_entry in ctx.guild.bans():
            if ban_entry.user.id == user_id:
                await ctx.guild.unban(ban_entry.user)
                embed = await self.use.create("✅ Sucesso!", f"<@{user_id}> desbanido!")
                await self.use.log_save(f"{ctx.author.name} desbaniu um usuario, usuario desbanido: {user_id}")
                await ctx.send(embed=embed)
                return
        
        embed = await self.use.create("Erro:", "❌ Usuário não encontrado na lista de bans.")
        await ctx.send(embed=embed)
  
    """ _ _ _ _ _ _ _ _ _ Economy methods _ _ _ _ _ _ _ _ _"""

    @commands.command(name="addmoney", aliases=["add money"])
    @commands.has_permissions(administrator=True)
    async def addmoney_prefix(self, ctx, user: Member, money: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        await self.db.update_field(user_id, 'money', money)
        embed = await self.use.create(f"BKZ adicionado por {ctx.author.mention}", f"{money:,} BKZ foram adicionados a {use.name}")
        await self.use.log_save(f"BKZ adicionado por {ctx.author.name}, BKZ foram adicionados a {use.name}, BKZ: {money:,}")
        await ctx.send(embed=embed)

    """ _ _ _ _ _ _ _ _ _ role methods _ _ _ _ _ _ _ _ _"""
    
    @commands.command(name="addrole", aliases=["addcargo", "add cargo", "add role"])
    @commands.has_permissions(administrator=True)
    async def add_role_prefix(self, ctx, user: Member, role: Union[discord.Role, int]):
        if isinstance(role, int):
            sucess = await self.use.add_role(user, role)
            embed = await self.use.create("Cargo adicionado", f"cargo adicionado a {user.name}")
            await ctx.send(embed=embed)
            return
        sucess = await user.add_roles(role)
        embed= await self.use.create("cargo adicionado", f"cargo adicionado a {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="romverole", aliases=["removecargo", "remove cargo", "remove role"])
    @commands.has_permissions(administrator=True)
    async def remove_role_prefix(self, ctx, user: Member, role: Union[discord.Role, int]):
        if isinstance(role, int):
            sucess = await self.use.remove_role(user, role)
            embed = await self.use.create("Cargo removido", f"cargo removido de {user.name}")
            await ctx.send(embed=embed)
            return
        
        sucess = await user.remove_roles(role)
        embed= await self.use.create("cargo removido", f"cargo removido de {user.name}")
        await ctx.send(embed=embed)

    @commands.command(name="limpar cargo", aliases=["limparcargo", "lc"])
    @commands.has_permissions(administrator=True)
    async def remove_all_role_prefix(self, ctx, role: Union[discord.Role, int]):
        if isinstance(role, int):
            role = await ctx.guild.get_role(role)
        if not isinstance(role, discord.Role):
            await ctx.send("❌ Cargo inválido ou não encontrado.")
            return

        message = ""
        acount = 0
        for member in role.members:
            sucess = await member.remove_roles(role)
            message += f"{member.mention}\n"
            acount +=1
        embed = await self.use.create("Cargo removido", f"cargo removido de {acount} usuarios\n\n{message}")
        await ctx.send(embed=embed)
    
    @commands.command(name="configurações", aliases=["config"])
    @commands.has_permissions(administrator=True)
    async def configs_prefix(self, ctx):
        try:
            configs = dbs_controler.load_all_configs()
            translater = dbs_controler.load_translater()
            configs_view = ConfigView()
            embed = await self.use.create(
                "**painel de condifuração:**",
                "Principais sistemas do bot, cuidado ao mexer!!\n\nClique no botão para ver as demais configurações desse sistema."
            )
            await ctx.channel.send(embed=embed, view=configs_view)
        except Exception as e:
            print(e)

    """slash methods (app)"""
    
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

    @app_commands.command(name="ban", description="Bane um usuario do servidor")
    @app_commands.describe(target="alvo")
    @app_commands.checks.has_permissions(administrator=True)
    async def ban_slash(self, interaction, target: Member, reason: str = ""):
        embed = await self.use.create("Comando de ban", "Em desenvolvimento")
        await interaction.response.send_message(embed=embed)

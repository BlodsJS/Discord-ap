from . import BaseCommands
import discord
import typing
from discord.ext import commands
from discord import app_commands, Member
import re
import logging

logger = logging.getLogger(__name__)

class AdminCommands(BaseCommands):
    @commands.command(name="addxp")
    @commands.has_permissions(administrator=True)
    async def addxp_prefix(self, ctx, user: Member, xp: int):
        user_id= str(user.id)
        user_data = await self.db.get_user_data(user_id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        need = (user_data["level"]**2) *taxa +100
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
        logger.info(f"XP adicionado por: {ctx.author.name}, para {user.name} ")
        await ctx.send(embed=embed)

    @commands.command(name="addlevel")
    @commands.has_permissions(administrator=True)
    async def addlevel_prefix(self, ctx, user: Member, level: int):
        user_id= str(user.id)
        await self.db.increment_level(user_id, level)
        embed = await self.use.create(f"Level adicionado por {ctx.author.mention}", f"✅ {level} level adicionados para {user.mention}")
        logger.info(f"Level adicionado por: {ctx.author.name}, para {user.name} ")
        await ctx.send(embed=embed)
        
    @commands.command(name="removexp")
    @commands.has_permissions(administrator=True)
    async def removexp_prefix(self, ctx, user: Member, xp: int):
        user_id= str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = xp
        if user_data["xp"] < xp:
        	xp = user_data["xp"] - user_data["xp"] +1
        await self.db.retirar_xp(user_id, xp)
        embed = await self.use.create(f"XP removido por {ctx.author.mention}", f"✅ {i} XP removidos para {user.mention}")
        logger.info(f"XP removido por: {ctx.author.name}, de {user.name} ")
        await ctx.send(embed=embed)
        
    @commands.command(name="removelevel")
    @commands.has_permissions(administrator=True)
    async def removelevel_prefix(self, ctx, user: Member, level: int):
        user_id= str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = level
        if user_data["level"] < level:
        	level = user_data["level"] - user_data["level"] +1
        await self.db.retirar_level(user_id, level)
        embed= await self.use.create(f"Level removido por {ctx.author.mention}", f"✅ {i} level removidos para {user.mention}")
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
        
        
    @commands.command(name="addchannel", aliases=["ac"])
    @commands.has_permissions(administrator=True)
    async def addchannel_prefix(self, ctx, user: Member, level: int):
    	pass
    	
    	
    #barras
    @app_commands.command(name="addxp", description="Adiciona XP a um usuário")
    @app_commands.describe(user="Usuário", xp="Quantidade de XP")
    @app_commands.checks.has_permissions(administrator=True)
    async def addxp_slash(self, interaction, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
        need = (user_data["level"]**2) *taxa +100
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
        embed = await self.use.create(f"XP adicionado por:{interaction.user.mention}", f"✅ {i} XP adicionados para {user.mention}")
        logger.info(f"XP adicionado por:{interaction.user.name}, para {user.name}")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="addlevel", description="Adiciona level a um usuário")
    @app_commands.describe(user="Usuário", level="Quantidade de levels")
    @app_commands.checks.has_permissions(administrator=True)
    async def addlevel_slash(self, interaction, user: Member, level: int):
        user_id = str(user.id)
        
        await self.db.increment_level(user_id, level)
        embed = await self.use.create(f"Level adicionado por {interaction.user.mention}", f"✅ {level} level adicionados para {user.mention}")
        logger.info(f"Level adicionado por:{interaction.user.name}, para {user.name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="removexp", description="remove xp de um usuário")
    @app_commands.describe(user="Usuário", xp="Quantidade de xp")
    @app_commands.checks.has_permissions(administrator=True)
    async def removexp_slash(self, interaction, user: Member, xp: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = xp
        if user_data["xp"] < xp:
        	xp = user_data["xp"] - user_data["xp"] +1
        await self.db.retirar_xp(user_id, xp)
        embed = await self.use.create(f"XP removido por{interaction.user.mention}", f"✅ {i} XP removidos para {user.mention}")
        logger.info(f"XP removido por:{interaction.user.name}, de {user.name}")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="removelevel", description="Adiciona level a um usuário")
    @app_commands.describe(user="Usuário", level="Quantidade de levels")
    @app_commands.checks.has_permissions(administrator=True)
    async def removelevel_slash(self, interaction, user: Member, level: int):
        user_id = str(user.id)
        user_data = await self.db.get_user_data(user_id)
        i = level
        if user_data["level"] < level:
        	level = user_data["level"] - user_data["level"] +1
        await self.db.retirar_level(user_id, level)
        embed= await self.use.create(f"Level removido por {interaction.user.mention}", f"✅ {i} level removidos para {user.mention}")
        logger.info(f"Level removido por:{interaction.user.name}, de {user.name}")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="reset", description="reseta um user ou todos")
    @app_commands.describe(target="alvo")
    @app_commands.checks.has_permissions(administrator=True)
    async def reset_slash(self, interaction, target: Member or str = None):
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
        
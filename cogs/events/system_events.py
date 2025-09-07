from . import BaseEventCog
from discord import Guild
import discord
from discord.ext import commands, tasks
import logging

logger = logging.getLogger(__name__)

class SystemEvents(BaseEventCog):
    
    @commands.Cog.listener()
    async def on_ready(self):
    	#await self.c_db.create()
    	print(self.c_db.dados)
    	await self.repo_movs.start()
    
    @commands.Cog.listener()
    async def on_disconnect(self):
    	await self.c_db._salvar_dados()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            logger.info("aqui está o erro")
            embed = await self.use.create("Erro:","❌ Você não tem permissão para usar este comando!")
            await ctx.send(embed=embed)
        elif isinstance(error, commands.CommandNotFound):
            logger.info("nao reconhece comando")
            embed = await self.use.create("Erro","⚠️ Comando não encontrado. Use `b!help` para ver a lista de comandos.")
            await ctx.send(embed=embed)
          
    @commands.Cog.listener()
    async def on_member_join(self, member):
        
        if member.bot:
            return
        data = self.dbs_controler.load_events("events")
        msg_template = " ".join(data["member_join"]["msg"])
        msg = f"{member.mention} | {msg_template}"
        
        channel = await self.bot.fetch_channel(1378829047370612746)
        await channel.send(msg)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        try:
          custom_id = interaction.data.get("custom_id", "")
          
          if custom_id.startswith("fechar_thread_"): 
              thread_id = int(custom_id.split("_")[-1])
              thread = interaction.guild.get_thread(thread_id)
              if not thread:
                  logger.info("thread não encontrada")
                  return
              if interaction.user == thread.owner or interaction.user.guild_permissions.manage_threads:
                  await thread.delete()
                  
              else:
                  await interaction.response.send_message("Você não tem permissão para fechar esta thread!", ephemeral=True)
        except Exception as e:
            logger.info(f"Erro no on_interaction: {e}", exc_info=True)
          
    @tasks.loop(minutes=5)
    async def box_check(self):
        if self.box >= 300:
            logger.info("a caixa chegou na meta")
            self.box = 0
            return
        else:
            logger.info(f"a caixa ainda não tocou na meta: {self.box}")
            return
          
    @tasks.loop(hours=24)
    async def repo_movs(self):
        try:
            channel = self.bot.get_channel(1378828994866184352)
            guild = self.bot.get_guild(1264448780950831197)
            
        except Exception as e:
            logger.info(f"Erro no repo_movs: {e}")

    async def repo_task(channel, guild):

        sucess = await self.use.ranking_chats(guild, 1396505115527217284)
        embed = await self.use.create("📊 **Relatório Mensal — Interação no Servidor**",sucess)
        await channel.send(embed=embed)
        

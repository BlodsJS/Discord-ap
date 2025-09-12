from . import BaseEventCog
from discord import Message, Member
from discord.ext import commands
import logging
import random
import discord

logger = logging.getLogger(__name__)
logger.info("Message carregado")

class MessageEvents(BaseEventCog):
     
     @commands.Cog.listener()
     async def on_message(self, message: Message):
            if message.author.bot or not message.guild:
                return
            if self.bot.user.mentioned_in(message):
                texts = self.dbs_controler.load_mind("answers")
                msg = random.choice(texts)
                await message.reply(msg)
            
            user_id = str(message.author.id)
            user_data = await self.db.get_user_data(user_id)
            await self.db.increment_message_count(user_id)
            # Verificar cooldown
            canais = self.c_db.get_canais(message.guild.id, "text")
            thread_canais = self.c_db.get_canais(message.guild.id, "thread")
            canais.extend(thread_canais)
            
            if message.channel.id not in canais:
                return
            if await self.use.has_role(message.author, 1378828943758463101):
                return
            
            self.box +=1
            taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
            box_teste = await self.use.box_check(message.channel, user_data, self.box, self.db, taxa)
            
            if box_teste:
                logger.info(f"Caixa funcionando {box_teste}")
                
                self.box = 0
            if self.cooldown_cache.get(user_id):
                return
            if await self.use.has_role(message.author, 1347726055892455504):
                return
                
            try:
                member = message.author
                amplifier = await self.use.amplifier_role(message.author)
                logger.info(f"amplificador: {amplifier}")
                xp_to_add = 20*amplifier
                await self.db.increment_xp(user_id, xp_to_add)
                

                #Get user profile and levels
                
                user_data = await self.db.get_user_data(user_id)
                taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
                money = random.randint(500, 1100)
                await self.db.increment_money(user_id, money)
                #await self.db.update_field(user_id,'money', money)
                xp_need = await self.use.xp_calc(user_data["level"], taxa)
                if user_data["xp"] >= xp_need:
                    gains = await self.use.xp_button(user_data["xp"], user_data["level"])
                    sucess = await self.use.check_role(gains[2], member)
                    await self.db.increment_level(user_id, gains[0])
                    await self.db.set_field("xp", user_id, gains[1])
                    if sucess:
                        name = f"<@&{sucess}>"
                        await self._notify_level_up(message.author, message, gains[2], name)
                self.cooldown_cache[user_id] = True
            except Exception as e:
                logger.info(f"Erro em mensagem de {message.author} em message_events.py: {e}")
                
      
     @commands.Cog.listener()
     async def on_message_delete(self, message):
         try:
             channel = self.bot.get_channel(1378828998921945339)
             embed = await self.use.create(f"Mensagem de {message.author} foi deletada em {message.channel.mention}", f"> {message.content}", discord.Color.red())
             await channel.send(embed=embed) 
           
         except Exception as e:
             logger.info(f"Erro na leitura de mensagem deletada: {e}")

     @commands.Cog.listener()
     async def on_message_edit(self, before, after):
         if before.content != after.content:
             channel = self.bot.get_channel(1378828998921945339)
             embed = await self.use.create(f"Mensagem editada por {after.author} em {after.channel.mention}",f"Antes:\n> {before.content}\n\nDepois:\n> {after.content}",discord.Color.yellow())
             await channel.send(embed=embed)
     
     async def _notify_level_up(self, member: Member, message, new_level, role):
            channel = self.bot.get_channel(message.channel.id)
       
            
            if member.id in self.users:
                if new_level in [5, 10, 15, 20, 25, 30, 40, 50, 65, 70, 85, 100]:
                    embed = await self.use.create("👑 Ascensão Real", f"{self.users[member.id]} {member.mention}")
                    embed.add_field(
                        name="Novo patamar:",
                        value=f"Você acaba de alcançar o: {role}",
                        inline=False
                    )
                    await channel.send(embed=embed)
                    return
                  
            if str(new_level) in self.text.text_levels:
                text = self.text.text_levels[str(new_level)]
                msg = f"{text} {member.mention}"
                await channel.send(msg)
                return
            return
              
            


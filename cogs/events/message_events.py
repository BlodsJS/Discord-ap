from . import BaseEventCog
from discord import Message, Member
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class MessageEvents(BaseEventCog):
     
     @commands.Cog.listener()
     async def on_message(self, message: Message):
            if message.author.bot or not message.guild:
            	return
            user_id = str(message.author.id)
            user_data = await self.db.get_user_data(user_id)
            await self.db.increment_message_count(user_id)
            # Verificar cooldown
            if self.cooldown_cache.get(user_id):
            	return
            	
            try:
            	await self.db.increment_xp(user_id, 13)
            	user_data = await self.db.get_user_data(user_id)
            	taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
            	if user_data["xp"] >= (user_data["level"]**2) * taxa +100:
            		new_level = user_data["level"] +1
            		new_xp = max(user_data["xp"] - ((user_data["level"]**2) * 100), 0)
            		await self.db.update_field(user_id, "level", new_level)
            		await self.db.update_field(user_id, "xp", new_xp)
            		await self._notify_level_up(message.author, message, new_level)
            	
            	self.cooldown_cache[user_id] = True
            except Exception as e:
            	logger.info(f"Erro em mensagem de {message.author} em message_events.py: {e}")
     async def _notify_level_up(self, member: Member, message, new_level):
        	channel = self.bot.get_channel(message.channel.id)
        	
        	if new_level in self.level_messages:
        		msg = self.level_messages[new_level]
        	else:
        		msg = f"Parabéns, você subiu de nível. Não espere fogos de artifício ou tapetes vermelhos — afinal, você ainda está longe de ser digno de minha atenção. Mas siga em frente... quem sabe um dia você chega lá. Ou não. Aproveite seu mísero Level {new_level}, {member.mention}"
        	if member.id in self.users:
        		msg = f"voce upou, depois ponho mensagem melhor: {member.mention}"
        	
        	await channel.send(msg)


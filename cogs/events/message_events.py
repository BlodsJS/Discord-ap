from . import BaseEventCog
from discord import Message

class MessageEvents(BaseEventCog):
    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        
        # Verificar cooldown
        if self.cooldown_cache.get(user_id):
            return

        try:
            new_level, levels_gained = await self.level_sys.handle_xp_increase(user_id)
            if levels_gained > 0:
                await self._notify_level_up(message, new_level)
                
            self.cooldown_cache[user_id] = True
            
        except Exception as e:
            self.logger.error(f"Erro em mensagem de {message.author}: {e}")

    async def _notify_level_up(self, message, new_level):
        channel = self.bot.get_channel(message.channel.id)
        msg = await self.level_sys.create_level_up_message(
            message.author, 
            new_level
        )
        await channel.send(msg)


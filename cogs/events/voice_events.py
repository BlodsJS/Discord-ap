from . import BaseEventCog
from discord import Message, Member
from discord.ext import commands
from discord import VoiceState, Member
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VoiceEvents(BaseEventCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.voice_sessions = {}
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member.bot:
            return

        user_id = str(member.id)
        user_data = await self.db.get_user_data(user_id)
        now = datetime.now()

        # Entrou em um canal de voz
        if not before.channel and after.channel:
            self.voice_sessions[user_id] = now
            return

        # Saiu do canal de voz
        if before.channel and not after.channel:
            entry_time = self.voice_sessions.pop(user_id, None)
            if entry_time:
                time_spent = (now - entry_time).total_seconds()
                new = int(user_data["voice"] + time_spent)
                await self.db.update_field(user_id, "voice", new)
                xp_earned = int(time_spent/60)
                await self.db.increment_xp(user_id, xp_earned)
                self.logger.info(f"XP de voz concedido: {member} - {xp_earned} XP, por ficar {time_spent} segundos em Call")


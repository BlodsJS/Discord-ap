from . import BaseEventCog
from discord import VoiceState, Member
from datetime import datetime

class VoiceEvents(BaseEventCog):
    def __init__(self, bot):
        super().__init__(bot)
        self.voice_sessions = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        if member.bot:
            return

        user_id = str(member.id)
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
                xp_earned = await self.level_sys.handle_voice_xp(user_id, time_spent)
                self.logger.info(f"XP de voz concedido: {member} - {xp_earned} XP")


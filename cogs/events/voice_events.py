from . import BaseEventCog
from discord import Message, Member
from discord.ext import commands
from discord import VoiceState, Member
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
logger.info("Voice carregado")

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
                call_amplifier = await self.use.amplifier_calc(int(time_spent//60))
                taxa = await self.use.obter_taxa(self.processor.inicios, self.processor.fins, self.processor.valores, user_data["level"])
                await self.db.increment_voice(user_id, time_spent)
                amplifier = await self.use.amplifier_role(member)
                amplifier += call_amplifier
                
                logger.info(f"amplificador: {amplifier}, teste de amplificador para call: {call_amplifier}")
                #time_spent = (now - entry_time).total_seconds()
                
                canais = self.c_db.get_canais(member.guild.id, "voice")
                if before.channel.id not in canais:
                    return
                
                xp_earned = int(time_spent/30) *amplifier
                
                
                await self.db.increment_xp(user_id, xp_earned)
                user_data = await self.db.get_user_data(user_id)
                xp_need = await self.use.xp_calc(user_data["level"], taxa)
                if user_data["xp"] >= xp_need:
                    gains = await self.use.xp_button(user_data["xp"], user_data["level"])
                    await self.use.check_role(gains[2], member)
                    await self.db.increment_level(user_id, gains[0])
                    await self.db.set_field("xp", user_id, gains[1])
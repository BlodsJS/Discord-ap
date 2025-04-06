# utils/level_system.py
import logging
import discord
from typing import Dict, Tuple
from datetime import datetime
from discord import Member, TextChannel
from database import DatabaseManager

logger = logging.getLogger(__name__)

class LevelSystem:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.level_messages = {
            5: "Você deixou de ser um zero... para se tornar um um.",
            10: "Você é como uma vela na tempestade...",
            # ... (adicionar outras mensagens)
        }

    async def calculate_xp_required(self, level: int) -> int:
        return (level ** 2) * 100

    async def calculate_level_progress(self, current_xp: int, current_level: int) -> Tuple[int, int, int]:
        xp_required = await self.calculate_xp_required(current_level)
        progress = min(current_xp / xp_required * 100, 100)
        return current_xp, xp_required, progress

    async def handle_xp_increase(self, user_id: str, xp_amount: int = 15) -> Tuple[int, int]:
        user_data = await self.db.get_user_data(user_id)
        new_xp = user_data['xp'] + xp_amount
        new_level = user_data['level']
        levels_gained = 0

        while True:
            xp_needed = await self.calculate_xp_required(new_level)
            if new_xp < xp_needed:
                break
            new_xp -= xp_needed
            new_level += 1
            levels_gained += 1

        await self.db.full_update_user(
            user_id,
            xp=new_xp,
            level=new_level
        )
        return new_level, levels_gained

    async def handle_voice_xp(self, user_id: str, time_spent: int) -> int:
        xp_earned = time_spent // 30  # 1 XP a cada 30 segundos
        await self.db.increment_xp(user_id, xp_earned)
        return xp_earned

    async def create_level_up_message(self, member: Member, new_level: int) -> str:
        base_message = self.level_messages.get(new_level, 
            f"Parabéns {member.mention}, você alcançou o nível {new_level}!"
        )
        
        if new_level in [25, 50, 100]:
            return f"🌟 {base_message}"
        return base_message
    async def get_data(self, user_id: str):
    	user_data = await self.db.get_user_data(user_id)
    	return user_data

    @staticmethod
    def calculate_rank(roles: list, rank_priority: list) -> str:
        for rank in rank_priority:
            if any(role.name == rank for role in roles):
                return rank
        return "Não ranqueado"

# Uso exemplo:
# level_system = LevelSystem(db_manager)
# new_level, levels_gained = await level_system.handle_xp_increase(str(user.id))


from discord.ext import commands
from database import DatabaseManager
from utils.level_system import LevelSystem
from cachetools import TTLCache

class BaseEventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.level_sys = LevelSystem(self.db)
        self.cooldown_cache = TTLCache(maxsize=1000, ttl=80)


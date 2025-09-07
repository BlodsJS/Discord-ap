from discord.ext import tasks, commands
from utils.level_system import LevelSystem
import logging

logger = logging.getLogger(__name__)
logger.info("Tasks carregado")

class BackgroundTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.level_sys = LevelSystem(bot.db)

    @tasks.loop(minutes=5)
    async def update_leaderboards(self):
        self.logger.info("Atualizando rankings...")
        await self.level_sys.refresh_leaderboard_cache()

    @tasks.loop(hours=1)
    async def backup_database(self):
        self.logger.info("Realizando backup do banco...")
        await self.bot.db.create_backup()


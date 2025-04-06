from discord.ext import commands
from database import DatabaseManager
from utils.image_processor import ImageProcessor
from utils.level_system import LevelSystem

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.processor = ImageProcessor()
        self.level_sys = LevelSystem(self.db)


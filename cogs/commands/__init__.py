from discord.ext import commands
from database import DatabaseManager
from utils.image_processor import ImageProcessor
from utils.level_system import LevelSystem
from utils.useful_system import UsefulSystem
from utils.help_text import TextSystem
from utils.channel_system import ChannelSystem

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.processor = ImageProcessor()
        self.level_sys = LevelSystem(self.db)
        self.use = UsefulSystem()
        self.ht = TextSystem()
        self.c_db = ChannelSystem()


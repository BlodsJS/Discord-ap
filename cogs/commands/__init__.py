from discord.ext import commands
from database import DatabaseManager
from utils.image_processor import ImageProcessor
from utils.useful_system import UsefulSystem
from utils.help_text import TextSystem
from utils.channel_system import ChannelSystem
from utils.level_system import LevelSystem
from cachetools import TTLCache
from utils.handlers.dbs_handler import dbs_controller
from utils.handlers.level_handler import LevelHandler
from utils.handlers.roles_handler import roles_controller
from utils.handlers.image_top_handler import top_image
from utils.handlers.teste_badge import badges_controller

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self.processor = ImageProcessor()
        self.level_sys = LevelSystem(self.db)
        self.use = UsefulSystem()
        self.text = TextSystem()
        self.c_db = ChannelSystem()
        self.cooldown_cache = TTLCache(maxsize=1000, ttl=3600)
        self.db_controler = dbs_controller
        self.level_controller = LevelHandler
        self.roles_controller = roles_controller
        self.top_image = top_image
        self.badges_controller = badges_controller

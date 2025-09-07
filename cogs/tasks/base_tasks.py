from discord.ext import commands

class BaseTask(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
      
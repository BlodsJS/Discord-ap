from .commands.basic import BasicCommands
from .commands.profile import ProfileCommands
from .commands.admin import AdminCommands

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
    await bot.add_cog(ProfileCommands(bot))
    await bot.add_cog(AdminCommands(bot))


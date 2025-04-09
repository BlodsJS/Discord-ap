from .commands.basic import BasicCommands
from .commands.profile import ProfileCommands
from .commands.admin import AdminCommands
from .events.system_events import SystemEvents

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
    await bot.add_cog(ProfileCommands(bot))
    await bot.add_cog(AdminCommands(bot))
    await bot.add_cog(SystemEvents(bot))
    


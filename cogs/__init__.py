from .commands.basic import BasicCommands
from .commands.profile import ProfileCommands
from .commands.admin import AdminCommands
from .events.system_events import SystemEvents
from .events.message_events import MessageEvents
from .events.voice_events import VoiceEvents
import logging

logger = logging.getLogger(__name__)

async def setup(bot):
    #cogs
    
    await bot.add_cog(BasicCommands(bot))
    logger.info("Comandos Basicos inicializados")
    
    await bot.add_cog(ProfileCommands(bot))
    logger.info("Comandos Profile inicializados")
    
    await bot.add_cog(AdminCommands(bot))
    logger.info("Comandos Admin inicializados")
    
    await bot.add_cog(SystemEvents(bot))
    logger.info("SystemEvents inicializado")
    
    await bot.add_cog(MessageEvents(bot))
    logger.info("MessageEvents inicializado")
    
    await bot.add_cog(VoiceEvents(bot))
    logger.info("VoiceEvents inicializado")
    
    #config adicional
    
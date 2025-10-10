from .commands.basic import BasicCommands
from .commands.profile import ProfileCommands
from .commands.admin import AdminCommands
from .events.system_events import SystemEvents
from .events.message_events import MessageEvents
from .events.voice_events import VoiceEvents
from .commands.house import HouseCommands
from .commands.economy import EconomyCommands
from .tasks.teste_tasks import BackgroundTasks
from utils.handlers.timer_handler import timer_controller

import logging

logger = logging.getLogger(__name__)
#cmdTimer = TimerManager()
async def setup(bot):
    #cogs
    bot.timer_controller = timer_controller
    await bot.add_cog(BasicCommands(bot)) #passo aqui o cmdTimer
    #logger.info("Comandos Basicos inicializados")
    
    await bot.add_cog(ProfileCommands(bot)) #passo aqui o cmdTimer
    #logger.info("Comandos Profile inicializados")
    
    await bot.add_cog(AdminCommands(bot)) #passo aqui o cmdTimer
    #logger.info("Comandos Admin inicializados")

    await bot.add_cog(EconomyCommands(bot))

    await bot.add_cog(HouseCommands(bot))
    
    await bot.add_cog(SystemEvents(bot))
    #logger.info("SystemEvents inicializado")
    
    await bot.add_cog(MessageEvents(bot))
    #logger.info("MessageEvents inicializado")
    
    await bot.add_cog(VoiceEvents(bot))
    #logger.info("VoiceEvents inicializado")
    
    await bot.add_cog(BackgroundTasks(bot))
    #logger.info("Tasks System inicializado")

    #teste de carregamento de cogs
    await bot.load_extension("cogs.commands.admin_commands")

    #adiciono aqui o carregamento das tasks exatamente como os outros cogs
     #passo aqui o cmdTimer
    
    #config adicional
    
from . import BaseEventCog
from discord import Guild

class SystemEvents(BaseEventCog):
    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info(f"Bot conectado como {self.bot.user.name}")
        await self.db.connect()
        await self._start_background_tasks()

    @commands.Cog.listener()
    async def on_disconnect(self):
        self.logger.info("Executando shutdown seguro...")
        await self.db.close()
        await self.bot.http_session.close()

    async def _start_background_tasks(self):
        if not hasattr(self.bot, 'background_tasks'):
            self.bot.background_tasks = {
                'status_rotation': self._status_rotation_task(),
                'cache_cleanup': self.level_sys.cache_cleanup()
            }
            for task in self.bot.background_tasks.values():
                self.bot.loop.create_task(task)

    async def _status_rotation_task(self):
        while True:
            await self._change_bot_status()
            await asyncio.sleep(120)


# main.py
import os
import aiohttp
import logging
import asyncio
import discord
from discord.ext import commands
from config import Config
from cogs import setup as setup_cogs



os_path_bc = os.getcwd()
# ************************** CONFIGURING OF LOGGER **************************
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('bot.main')
logger.info(f"Diretu00f3rio atual: {os_path_bc}")


# ************************** MAIN BOT CLASS **************************
class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=self.get_prefix,
            intents=Config.INTENTS,
            help_command=None,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=False,
                replied_user=True
            )
        )
        self.db = None
        self.http_session = None

    async def get_prefix(self, message: discord.Message) -> str:
        """Dynamic prefix handler"""
        return Config.PREFIXES

    async def setup_hook(self) -> None:
        """Initialize extensions and background tasks"""
        await self.load_essentials()
        await setup_cogs(self)
        await self.tree.sync()
        logger.info(f'Carregado {len(self.cogs)} cogs e {
                    len(self.commands)} comandos')

    async def load_essentials(self) -> None:
        """Load core components"""
        from database import DatabaseManager
        self.db = DatabaseManager()
        await self.db.connect()
        self.http_session = aiohttp.ClientSession()
        logger.info('Componentes essenciais carregados')

    async def on_ready(self) -> None:
        """Bot startup handler"""
        logger.info(f'Conectado como: {self.user.name} | ID: {self.user.id}')
        logger.info(f' Latência: {round(self.latency * 1000)}ms')

    async def close(self) -> None:
        """Clean shutdown procedure"""
        await self.shutdown()
        await super().close()
# ************************** API FINALIZATION **************************
    async def shutdown(self) -> None:
        """Graceful shutdown sequence"""
        logger.info('Iniciando desligamento seguro...')

        # closes section HTTP
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
            logger.info(' Seção HTTP encerrada')

        # closes connection with the bank 
        if self.db and self.db.connection:
            await self.db.close()
            logger.info('Conexão com banco de dados fechada')

        # cancels all pending tasks
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        logger.info('Todas as tasks foram canceladas')


# ************************** DEF DE INICIALIZAÇÃO **************************
async def main():
    """Entry point"""
    bot = Bot()
    try:
        await bot.start(Config.TOKEN)
    except KeyboardInterrupt:
        logger.info("Desligamento solicitado via teclado")
    except Exception as e:
        logger.error(f"Erro crítico: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())

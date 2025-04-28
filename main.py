# main.py
import os
import aiohttp
import logging
import asyncio
import discord
from discord.ext import commands
from config import Config
from cogs import setup as setup_cogs
print("Diretu00f3rio atual:", os.getcwd())

# Configurau00e7u00e3o bu00e1sica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('bot.main')


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
        return commands.when_mentioned_or(*Config.PREFIXES)(self, message)

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
        logger.info(f'Latu00eancia: {round(self.latency * 1000)}ms')
        await self.change_presence(activity=discord.Game(name="Inicializando..."))

    async def close(self) -> None:
        """Clean shutdown procedure"""
        await self.shutdown()
        await super().close()

    async def shutdown(self) -> None:
        """Graceful shutdown sequence"""
        logger.info('Iniciando desligamento seguro...')

        # Encerrar sessu00e3o HTTP
        if self.http_session and not self.http_session.closed:
            await self.http_session.close()
            logger.info('Sessu00e3o HTTP encerrada')

        # Fechar conexu00e3o do banco
        if self.db and self.db.connection:
            await self.db.close()
            logger.info('Conexu00e3o com banco de dados fechada')

        # Cancelar tasks pendentes
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        logger.info('Todas as tasks foram canceladas')


async def main():
    """Entry point"""
    bot = Bot()
    try:
        await bot.start(Config.TOKEN)
    except KeyboardInterrupt:
        logger.info("Desligamento solicitado via teclado")
    except Exception as e:
        logger.error(f"Erro cru00edtico: {e}")
    finally:
        if not bot.is_closed():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())

# inicio do db
import aiosqlite
import logging
from typing import Optional, Dict, Any, AsyncContextManager, List
from easy_pil import Editor, Canvas, Font, load_image_async
import cachetools
import asyncio
import discord

logger = logging.getLogger(__name__)

class DatabaseManager:
    _instance = None
    _initialized = False

    def __new__(cls, db_path: str = 'xp_data.db'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_path = db_path
            cls._instance.connection = None
            cls._instance.lock = asyncio.Lock()
        return cls._instance

    async def _initialize(self):
        """Inicializau00e7u00e3o assu00edncrona"""
        if not self._initialized:
            self.connection = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            self._initialized = True
            logger.info("DatabaseManager inicializado")

    async def connect(self) -> None:
        """Estabelece conexu00e3o com o banco de dados"""
        async with self.lock:
            # Verifica se a conexu00e3o estu00e1 fechada ou nu00e3o existe
            if self.connection is None or not self.connection.is_alive:
                if self.connection is not None:
                    await self.connection.close()
                self.connection = await aiosqlite.connect(self.db_path)
                await self._create_tables()
                logger.info("Conexu00e3o com o banco estabelecida")

    async def _create_tables(self):
        async with self.connection.execute('''
            CREATE TABLE IF NOT EXISTS xp_data (
                user_id TEXT PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                message INTEGER DEFAULT 0,
                voice INTEGER DEFAULT 0,
                money INTEGER DEFAULT 0,
                rep INTEGER DEFAULT 0
            )
        '''):
            await self.connection.commit()

    async def _execute_query(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        await self.connect()  # Garante que a conexu00e3o estu00e1 ativa
        async with self.lock:
            try:
                async with self.connection.execute(query, params) as cursor:
                    await self.connection.commit()
                    if query.strip().upper().startswith('SELECT'):
                        return await cursor.fetchone()
                    return None
            except aiosqlite.Error as e:
                logger.error(f"Erro na query: {query} | Params: {
                             params} | Erro: {e}")
                raise

    # Mu00e9todo genu00e9rico seguro para atualizau00e7u00f5es
    async def updater_field(self, user_id: str, field: str, value: Any) -> bool:
        await self.connect()
        allowed_fields = {'xp', 'level', 'message', 'voice', 'money', 'rep'}
        if field not in allowed_fields:
            raise ValueError(f"Campo invu00e1lido: {
                             field}. Permitidos: {allowed_fields}")

        query = f"""
            UPDATE xp_data
            SET {field} = ?
            WHERE user_id = ?
        """
        try:
            result = await self._execute_query(query, (value, user_id))
            logger.info(f"sucesso ao atualizar {field} para {user_id}")
            return True
        except Exception as e:
            logger.error(f"Falha ao atualizar {field} para {user_id}: {e}")
            return False
          
    async def update_field(self, user_id: str, field: str, value: Any) -> bool:
        await self.connect()
        allowed_fields = {'xp', 'level', 'message', 'voice', 'money', 'rep'}
        if field not in allowed_fields:
            raise ValueError(f"Campo invu00e1lido: {
                             field}. Permitidos: {allowed_fields}")
        if field == "voice":
            value = value*60

        query = f"""
            UPDATE xp_data
            SET {field} = ?
            WHERE user_id = ?
        """
        try:
            result = await self._execute_query(query, (value, user_id))
            logger.info(f"sucesso ao atualizar {field} para {user_id}")
            return True
        except Exception as e:
            logger.error(f"Falha ao atualizar {field} para {user_id}: {e}")
            return False

    # Mu00e9todos especu00edficos para melhor legibilidade
    async def increment_voice(self, user_id: str, amount: int) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET voice = voice + ? WHERE user_id = ?",
            (amount, user_id)
        )
      
    async def increment_xp(self, user_id: str, amount: int) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET xp = xp + ? WHERE user_id = ?",
            (amount, user_id)
        )

    async def increment_level(self, user_id: str, amount: int) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET level = level + ? WHERE user_id = ?",
            (amount, user_id)
        )

    async def retirar_xp(self, user_id: str, amount: int) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET xp = xp - ? WHERE user_id = ?",
            (amount, user_id)
        )

    async def retirar_level(self, user_id: str, amount: int) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET level = level - ? WHERE user_id = ?",
            (amount, user_id)
        )

    async def increment_message_count(self, user_id: str) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET message = message + 1 WHERE user_id = ?",
            (user_id,)
        )

    async def update_level(self, user_id: str, new_level: int) -> bool:
        return await self.update_field(user_id, 'level', new_level)

    # Mu00e9todo completo para atualizau00e7u00e3o complexa
    async def efull_update_user(self, user_id: str, **fields) -> bool:
        await self.connect()
        allowed_fields = {'xp', 'level', 'message', 'voice'}
        updates = []
        params = []

        for field, value in fields.items():
            if field in allowed_fields:
                updates.append(f"{field} = ?")
                params.append(value)

        if not updates:
            return False

        query = f"""
            UPDATE xp_data
            SET {', '.join(updates)}
            WHERE user_id = ?
        """
        params.append(user_id)

        return await self._execute_query(query, tuple(params))

    async def get_user_data(self, user_id: str) -> Dict[str, Any]:
        await self.connect()

        async with self.connection.execute(
            "SELECT xp, level, message, voice, money, rep FROM xp_data WHERE user_id = ?",
            (user_id,)
        ) as cursor:

            row = await cursor.fetchone()
            if row:
                user_data = {
                    "xp": row[0],
                    "level": row[1],
                    "message": row[2],
                    "voice": row[3],
                    "money": row[4],
                    "rep": row[5]
                }
                return user_data
            
            async with self.connection.execute(
                    "INSERT INTO xp_data (user_id, xp, level, message, voice, money, rep) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (user_id, 0, 1, 0, 0, 0, 0)
            ) as cursor:

                await self.connection.commit()
                return {
                    "xp": 0,
                    "level": 1,
                    "message": 0,
                    "voice": 0,
                    "money": 0,
                    "rep": 0
                }
                

    async def get_user_rank(self, user_id: str) -> int:
        # Primeiro, obtenha os dados do usuu00e1rio
        user_data = await self.get_user_data(user_id)
        user_level = user_data["level"]
        user_xp = user_data["xp"]
        query = """
                SELECT COUNT(*) + 1 as rank
                FROM xp_data
                WHERE level > ?
                        OR (level = ? AND xp > ?)
        """
        async with self.connection.execute(query, (user_level, user_level, user_xp)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 1

    async def top_users_field(self, field: str, offset: int = 0):
        await self.connect()
        try:
            # Consulta assu00edncrona ao banco de dados
            async with self.connection.execute(f'''
                SELECT user_id, {field}
                FROM xp_data
                ORDER BY {field} DESC
                LIMIT 10 OFFSET ?
                ''', (offset,)) as cursor:

                top_server = await cursor.fetchall()

            if not top_server:
                return
            return top_server

        except Exception as e:
            logging.error(f"Erro ao gerar ranking de {field}: {e}")
            return

    async def top_users(self, offset: int = 0):
        await self.connect()
        try:
            # Consulta assu00edncrona ao banco de dados
            async with self.connection.execute('''
                SELECT user_id, xp, level, message, voice
                FROM xp_data 
                ORDER BY level DESC, xp DESC
                LIMIT 5 OFFSET ?
                ''', (offset,)) as cursor:

                top_server = await cursor.fetchall()

            if not top_server:
                return discord.File(Editor(Canvas((580, 200), color="#131515")).image_bytes, "leaderboard.png")
            return top_server

        except Exception as e:
            logging.error(f"Erro ao gerar ranking: {e}")
            return discord.File(Editor(Canvas((580, 200), color="#131515")).image_bytes, "leaderboard.png")

    async def reset_xp(self):
        await self.connect()

        query = """
                UPDATE xp_data 
                SET 
                    xp = 0,
                    level = 1
            """
        try:
            async with self.connection.execute(query) as cursor:
                await self.connection.commit()
                return cursor.rowcount  # Retorna quantos usuu00e1rios foram resetados
        except Exception as e:
            logger.error(f"Erro ao resetar usuu00e1rios: {e}")
            return 0

    async def reset_user(self, user_id: str):
        await self.connect()
        query = """
                UPDATE xp_data 
                SET 
                    xp = 0,
                    level = 1
                WHERE user_id = ?
            """
        try:

            async with self.connection.execute(query, (user_id,)) as cursor:
                await self.connection.commit()
                return "Usuario resetado"  # Retorna quantos usuu00e1rios foram resetados
        except Exception as e:
            logger.error(f"Erro ao resetar usuu00e1rio: {e}")
            return 0

    async def close(self):
        async with self.lock:
            if self.connection and not await self.connection.close():
                await self.connection.close()
                logger.info("Conexu00e3o com o banco fechada")

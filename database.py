#inicio do db
import aiosqlite
import logging
from typing import Optional, Dict, Any, AsyncContextManager
import cachetools
import asyncio

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
        """Inicialização assíncrona"""
        if not self._initialized:
            self.connection = await aiosqlite.connect(self.db_path)
            await self._create_tables()
            self._initialized = True
            logger.info("DatabaseManager inicializado")
    async def connect(self) -> None:
        """Estabelece conexão com o banco de dados"""
        async with self.lock:
        	
	        if not self.connection or self.connection.close:
	            self.connection = await aiosqlite.connect(self.db_path)
	            await self._create_tables()
	            logger.info("Conexão com o banco estabelecida")

    async def _create_tables(self):
        async with self.connection.execute('''
            CREATE TABLE IF NOT EXISTS xp_data (
                user_id TEXT PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                message INTEGER DEFAULT 0,
                voice INTEGER DEFAULT 0
            )
        '''):
            await self.connection.commit()

    async def _execute_query(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        await self.connect()
        async with self.lock:
            if not self.connection or await self.connection.close():
                await self._initialize()
            
            try:
                async with self.connection.execute(query, params) as cursor:
                    await self.connection.commit()
                    if query.strip().upper().startswith('SELECT'):
                        return await cursor.fetchone()
                    return None
            except aiosqlite.Error as e:
                logger.error(f"Erro na query: {query} | Params: {params} | Erro: {e}")
                raise

    # Método genérico seguro para atualizações
    async def update_field(self, user_id: str, field: str, value: Any) -> bool:
        await self.connect()
        allowed_fields = {'xp', 'level', 'message', 'voice'}
        if field not in allowed_fields:
            raise ValueError(f"Campo inválido: {field}. Permitidos: {allowed_fields}")
        
        query = f"""
            UPDATE xp_data 
            SET {field} = ?
            WHERE user_id = ?
        """
        try:
            result = await self._execute_query(query, (value, user_id))
            return True
        except Exception as e:
            logger.error(f"Falha ao atualizar {field} para {user_id}: {e}")
            return False

    # Métodos específicos para melhor legibilidade
    async def increment_xp(self, user_id: str, amount: int) -> bool:
        await self.connect()
        return await self._execute_query(
            "UPDATE xp_data SET xp = xp + ? WHERE user_id = ?",
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

    # Método completo para atualização complexa
    async def full_update_user(self, user_id: str, **fields) -> bool:
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
            "SELECT xp, level, message, voice FROM xp_data WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
        print(row)
        return row


    async def close(self):
        async with self.lock:
            if self.connection and not await self.connection.close():
                await self.connection.close()
                logger.info("Conexão com o banco fechada")

import logging
import discord
from typing import Dict, Tuple, List
from datetime import datetime
from discord import Member, TextChannel
import aiofiles
import pathlib
import json
import asyncio

class ChannelSystem:
    def __init__(self, arquivo: str = 'canais.json'):
        self.arquivo = pathlib.Path(arquivo)
        print(self.arquivo)
        self.dados: Dict[str, Dict[str, List[int]]] = {}# Estrutura correta
        asyncio.create_task(self._carregar_dados())

    @classmethod
    async def create(cls, arquivo: str = 'canais.json'):
        """Factory method correto"""
        instance = cls(arquivo)
        await instance._carregar_dados()
        return instance

    async def _carregar_dados(self):
        try:
            async with aiofiles.open(self.arquivo, 'r') as f:
                conteudo = await f.read()
                self.dados = json.loads(conteudo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.dados = {}

    async def _salvar_dados(self):
        async with aiofiles.open(self.arquivo, 'w') as f:
            await f.write(json.dumps(self.dados, indent=4))

    # ... manter métodos inserir/apagar/get_canais ...
    async def inserir(self, guild_id: int, channel_id: int, field: str) -> bool:
        """Adiciona canal a um campo específico (text/voice)"""
        chave = str(guild_id)
        
        # Cria a estrutura se não existir
        if chave not in self.dados:
            self.dados[chave] = {"text": [], "voice": []}
        
        # Adiciona ao campo especificado
        if channel_id not in self.dados[chave][field]:
            self.dados[chave][field].append(channel_id)
            await self._salvar_dados()
            return True
        return False

    async def apagar(self, guild_id: int, channel_id: int, field: str) -> bool:
        """Remove canal de um campo específico"""
        chave = str(guild_id)
        
        if chave in self.dados and channel_id in self.dados[chave].get(field, []):
            self.dados[chave][field].remove(channel_id)
            await self._salvar_dados()
            return True
        return False

    def get_canais(self, guild_id: int, field: str) -> List[int]:
        """Retorna a lista de canais do campo especificado ou vazia"""
        return self.dados.get(str(guild_id), {}).get(field, [])
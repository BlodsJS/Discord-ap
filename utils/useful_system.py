import logging
import discord
from typing import Dict, Tuple
from datetime import datetime
from discord import Member, TextChannel
import bisect
from datetime import datetime
import pathlib
import json

logger = logging.getLogger(__name__)
logger.info("Useful carregado")

class UsefulSystem:
    def __init__(self, arquivo: str = 'log.txt'):
        self.cor = discord.Color.default()
        self.arquivo = pathlib.Path(arquivo)
        
    async def create(self, title, desc, color = None):
        color = self.cor if color is None else color
        embed = discord.Embed(
            title= title,
            description= desc,
            color= color
        )
        logger.info(f"objeto retornado na embed: {embed}")
        return embed
        
    async def obter_taxa(self, inicios, fins, valores, acount):
        idx = bisect.bisect_right(inicios, acount) - 1
        if idx >= 0 and acount < fins[idx]:
            return valores[idx]
        return 100  # Valor fora dos intervalos
    
    async def registrar_evento(self, texto: str, arquivo: str =  "log.txt"):
        """Registra um evento com timestamp no arquivo especificado."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{timestamp}] {texto}\n"
        with open(arquivo, "a", encoding="utf-8") as f:
            f.write(linha)
        
    async def has_role(member, role_id):
        user_role_ids = [role.id for role in member.roles]
        return role_id in user_role_ids

    def get_roles():
        with open("cargos.json") as f:
            return json.load(f)

    async def add_role(self, member, role_id):
        role = discord.utils.get(member.guild.roles, id= role_id)
        await member.add_roles(role)

    async def remove_role(self, member, role_id):
        role = discord.utils.get(member.guild.roles, id= role_id)
        await member.remove_roles(role)

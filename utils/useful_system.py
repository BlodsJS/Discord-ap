import logging
import discord
from typing import Dict, Tuple
from datetime import datetime
from discord import Member, TextChannel
import bisect

class UsefulSystem:
	def __init__(self):
		self.cor = discord.Color.default()	
	async def create(self, title, desc, color = None):
		color = self.cor if color is None else color
		embed = discord.Embed(
			title= title,
			description= desc,
			color= color
		)
		return embed
		
	async def obter_taxa(self, inicios, fins, valores, acount):
	    idx = bisect.bisect_right(inicios, acount) - 1
	    if idx >= 0 and acount < fins[idx]:
	        return valores[idx]
	    return 100  # Valor fora dos intervalos

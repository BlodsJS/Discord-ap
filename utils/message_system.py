import logging
import discord
from typing import Dict, Tuple
from datetime import datetime
from discord import Member, TextChannel

logger = logging.getLogger(__name__)

class MessageSystem:
	def __init__(self):
		self.messages = {
			"add xp": "Adiciona xp a um usuario (@user)"
		}
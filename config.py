import os
from discord import Intents

# Configurau00e7u00e3o centralizada


class Config:
    TOKEN = os.getenv("DISCORD_TOKEN")
    AI_TOKEN = os.getenv("AI_API_KEY")
    PREFIXES = ["b!", "B!"]

    INTENTS = Intents.default()
    INTENTS.message_content = True
    INTENTS.members = True

    PERSONALITY_FILE = "pers_bei.txt"
    DB_PATH = "xp_data.db"

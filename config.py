import os
from discord import Intents

from dotenv import load_dotenv
load_dotenv()

# centralized settings 


class Config:

    # bot token
    TOKEN = os.getenv("DISCORD_TOKEN")
    # ia token
    AI_TOKEN = os.getenv("AI_API_KEY")
    # bot prefix
    PREFIXES = ["b!", "B!"]

    # basic configs (commands)
    INTENTS = Intents.default()
    INTENTS.message_content = True
    INTENTS.members = True

    # extras configs
    PERSONALITY_FILE = "pers_bei.txt"
    DB_PATH = "xp_data.db"

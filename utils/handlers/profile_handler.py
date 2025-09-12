import random
import json
from handlers.dbs_handler import dbs_controler
from pathlib import Path

class ProfileHandler:
    
    @staticmethod
    def edit_profile(user_id: str, field: str, value: str):
        try:
            file_json = Path("utils/dbs/users_profile.json")
            profiles = dbs_controler.load_profiles
            if user_id not in profiles:
                profiles[user_id] = {}
            
            profiles[user_id][field] = value
            with open(file_json, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=4)
        except  Exception as e:
            logger.info(f"Erro na gravação: {e}")
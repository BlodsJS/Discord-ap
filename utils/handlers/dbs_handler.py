import json
from pathlib import Path

class dbs_controler:
    # Arquivos definidos como atributos de classe
    map_file = Path("utils/dbs/map.json")
    question_file = Path("utils/dbs/questons.json")
    users_tests_file = Path("utils/dbs/tests.json")
    all_configs_file = Path("utils/dbs/configs.json")
    standart_banner_file = Path("utils/dbs/standard_banners.json")
    profiles_file = Path("utils/dbs/users_profile.json")
    bei_mind_file = Path("utils/dbs/bei_mind.json")
    translater_file = Path("utils/dbs/translate.json")

    # ----------------------
    # Métodos de leitura
    # ----------------------
    @staticmethod
    def _load(path: Path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ----------------------
    # Métodos de escrita
    # ----------------------
    @staticmethod
    def _save(path: Path, data: dict | list):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    # ----------------------
    # Métodos de escrita por sistemas
    # ---------------------

    @staticmethod
    def load_users(field):
        data = dbs_controler._load(dbs_controler.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_roles(field):
        data = dbs_controler._load(dbs_controler.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_events(field):
        data = dbs_controler._load(dbs_controler.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_timers(field):
        data = dbs_controler._load(dbs_controler.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_house(field):
        data = dbs_controler._load(dbs_controler.all_configs_file)
        return data[field]

    @staticmethod
    def load_all_configs(field=None):
        data = dbs_controler._load(dbs_controler.all_configs_file)
        if field is None:
            return data
        return data.get(field)

    @staticmethod
    def load_map():
        return dbs_controler._load(dbs_controler.map_file)

    @staticmethod
    def load_questions():
        return dbs_controler._load(dbs_controler.question_file)
    
    @staticmethod
    def load_translater():
        return dbs_controler._load(dbs_controler.translater_file)

    @staticmethod
    def load_users_tests():
        return dbs_controler._load(dbs_controler.users_tests_file)

    @staticmethod
    def load_banners():
        return dbs_controler._load(dbs_controler.standart_banner_file)

    @staticmethod
    def load_profiles():
        return dbs_controler._load(dbs_controler.profiles_file)
    
    def load_mind(field):
        data = dbs_controler._load(dbs_controler.bei_mind_file)
        return data[field]
    # ----------------------
    # Métodos de escrita por sistemas
    # ----------------------
    def deep_update(original: dict, updates: dict):
        """Atualiza sub-dicionários recursivamente, preservando tudo que não é alterado"""
        for key, value in updates.items():
            if isinstance(value, dict) and key in original and isinstance(original[key], dict):
                deep_update(original[key], value)
            else:
                original[key] = value
    
    def update_users(db: dict, updates: dict):
        if "users" not in db:
            db["users"] = {}
        deep_update(db["users"], updates)

    def update_roles(db: dict, updates: dict):
        if "roles" not in db:
            db["roles"] = {}
        deep_update(db["roles"], updates)
    
    def update_events(db: dict, updates: dict):
        if "events" not in db:
            db["events"] = {}
        deep_update(db["events"], updates)
    
    def update_timers(db: dict, updates: dict):
        if "events" not in db:
            db["events"] = {}
        deep_update(db["events"], updates)
    
    def update_houses(db: dict, updates: dict):
        if "events" not in db:
            db["events"] = {}
        deep_update(db["events"], updates)
    
    
    @staticmethod
    def update_configs(updates: dict):
        """Atualiza chaves em configs.json"""
        data = dbs_controler._load(dbs_controler.all_configs_file)
        data.update(updates)  # mescla os valores
        dbs_controler._save(dbs_controler.all_configs_file, data)

    @staticmethod
    def replace_profiles(new_profiles: list):
        """Substitui completamente users_profile.json"""
        dbs_controler._save(dbs_controler.profiles_file, new_profiles)
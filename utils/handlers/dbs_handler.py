import json
from pathlib import Path

class dbs_controller:
    # Arquivos definidos como atributos de classe
    map_file = Path("utils/dbs/map.json")
    question_file = Path("utils/dbs/questons.json")
    users_tests_file = Path("utils/dbs/tests.json")
    all_configs_file = Path("utils/dbs/configs.json")
    standart_banner_file = Path("utils/dbs/standart_banners.json")
    profiles_file = Path("utils/dbs/users_profile.json")
    bei_mind_file = Path("utils/dbs/bei_mind.json")
    translater_file = Path("utils/dbs/translate.json")
    message_level_file = Path("utils/dbs/message_level.json")

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
    def load_users(field="users"):
        data = dbs_controller._load(dbs_controller.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_roles(field="roles"):
        data = dbs_controller._load(dbs_controller.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_events(field="events"):
        data = dbs_controller._load(dbs_controller.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_timers(field="timers"):
        data = dbs_controller._load(dbs_controller.all_configs_file)
        return data[field]
    
    @staticmethod
    def load_house(field="houses"):
        data = dbs_controller._load(dbs_controller.all_configs_file)
        return data[field]

    @staticmethod
    def load_all_configs():
        data = dbs_controller._load(dbs_controller.all_configs_file)
        return data

    @staticmethod
    def load_map():
        return dbs_controller._load(dbs_controller.map_file)

    @staticmethod
    def load_questions():
        return dbs_controller._load(dbs_controller.question_file)
    
    @staticmethod
    def load_translater():
        return dbs_controller._load(dbs_controller.translater_file)

    @staticmethod
    def load_users_tests():
        return dbs_controller._load(dbs_controller.users_tests_file)

    @staticmethod
    def load_banners():
        return dbs_controller._load(dbs_controller.standart_banner_file)

    @staticmethod
    def load_profiles():
        return dbs_controller._load(dbs_controller.profiles_file)
    @staticmethod
    def load_messages():
        return dbs_controller._load(dbs_controller.message_level_file)
    
    def load_mind(field):
        data = dbs_controller._load(dbs_controller.bei_mind_file)
        return data[field]
    # ----------------------
    # Métodos de escrita por sistemas
    # ----------------------
    
    @staticmethod
    def update_configs(updates: dict):
        
        data = dbs_controller._load(dbs_controller.all_configs_file)
        data.update(updates)  # mescla os valores
        dbs_controller._save(dbs_controller.all_configs_file, data)

    @staticmethod
    def update_profiles(updates):
        
        data = dbs_controller._load(dbs_controller.profiles_file)
        data.update(updates)
        dbs_controller._save(dbs_controller.profiles_file, data)
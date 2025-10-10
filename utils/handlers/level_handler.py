import bisect

class LevelHandler:
    
    rates = {
        range(1, 26): 20,
        range(26, 51): 20,
        range(51, 101): 35
    }
    
    ordened_intervals = sorted(
        [(r.start, r.stop, v) for r, v in rates.items()],
        key=lambda x: x[0]
    )
    initial = [interval[0] for interval in ordened_intervals]
    final = [interval[1] for interval in ordened_intervals]
    values = [interval[2] for interval in ordened_intervals]
    
    @staticmethod
    def get_rate(acount):
        idx = bisect.bisect_right(LevelHandler.initial, acount) - 1
        if idx >= 0 and acount < LevelHandler.final[idx]:
            return LevelHandler.values[idx]
        return 100  # Valor fora dos intervalos
    
    @staticmethod
    def xp_required(level:int, rate: int):
        xp_need = (level**2)*rate +100
        return xp_need
    
    @staticmethod
    def level_up(user_data:dict, xp_need):
        levels_gained = 0
        while user_data["xp"] >= xp_need:
            levels_gained +=1
            user_data["xp"] -= xp_need
            rate = LevelHandler.get_rate(user_data["level"]+levels_gained)
            xp_need = LevelHandler.xp_required(user_data["level"]+levels_gained, rate)
        
        user_data["level"] += levels_gained
        return user_data

    @staticmethod
    def check_xp(user_data: dict):
        rate = LevelHandler.get_rate(user_data["level"])
        xp_needed = xp_required(user_data["level"], rate)
        if user_data["xp"] >= xp_need:
            level_data = level_up(user_data, xp_needed)
            return level_data
        return None
    
    @staticmethod
    def gain_xp(user_data:dict, booster: float, xp_base: int):
        xp_gained = xp_base*booster
        user_data["xp"] += xp_gained
        rate = LevelHandler.get_rate(user_data["level"])
        xp_need = LevelHandler.xp_required(user_data["level"], rate)
        if user_data["xp"] >=xp_need:
            LevelHandler.level_up(user_data, xp_need)
        return user_data
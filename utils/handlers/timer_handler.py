import time
from discord.ext import commands

class timer_controller:
    cooldowns = {}
    
    
    @staticmethod
    def set_cooldown(user_id, command_name, cooldown_time):
        """Define o tempo de recarga de um comando para um usuário."""
        timer_controller.cooldowns[(user_id, command_name)] = time.time() + cooldown_time
    
    @staticmethod
    def is_on_cooldown(user_id, command_name):
        """Verifica se o comando está em recarga para o usuário."""
        key = (user_id, command_name)
        if key in timer_controller.cooldowns:
            if time.time() < timer_controller.cooldowns[key]:
                return True
            else:
                del timer_controller.cooldowns[key]  # Remove se o tempo de recarga expirou
        return False
    
    @staticmethod
    def get_time_left(user_id, command_name):
        """Retorna o tempo restante para o cooldown de um comando."""
        key = (user_id, command_name)
        if key in timer_controller.cooldowns:
            return max(0, timer_controller.cooldowns[key] - time.time())
        return 0

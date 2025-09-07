import asyncio
from collections import defaultdict

class TimerManager:
    def __init__(self):
        # Estrutura: {user_id: {command: seconds_remaining}}
        self.cooldowns = defaultdict(dict)
        self._lock = asyncio.Lock()

    async def set_cooldown(self, user_id: str, command: str, duration: int):
        async with self._lock:
            self.cooldowns[user_id][command] = duration

    async def get_cooldown(self, user_id: str, command: str) -> int:
        async with self._lock:
            return self.cooldowns.get(user_id, {}).get(command, 0)

    async def tick(self):
        """
        Decrementa os cooldowns a cada segundo. Deve ser rodada como uma task.
        """
        while True:
            await asyncio.sleep(1)
            async with self._lock:
                to_remove = []
                for user_id, commands in self.cooldowns.items():
                    for command, seconds in list(commands.items()):
                        if seconds <= 1:
                            commands.pop(command)
                        else:
                            commands[command] -= 1
                    if not commands:
                        to_remove.append(user_id)
                for user_id in to_remove:
                    self.cooldowns.pop(user_id)
                  
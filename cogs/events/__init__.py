from discord.ext import commands
from database import DatabaseManager
from utils.level_system import LevelSystem
from cachetools import TTLCache
from utils.useful_system import UsefulSystem
from utils.image_processor import ImageProcessor
from utils.channel_system import ChannelSystem


class BaseEventCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.processor = ImageProcessor()
        self.db = DatabaseManager()
        self.level_sys = LevelSystem(self.db)
        self.use = UsefulSystem()
        self.c_db = ChannelSystem()
        self.cooldown_cache = TTLCache(maxsize=1000, ttl=80)
        self.level_messages = {
	     	5: "Você deixou de ser um zero... para se tornar um um. Não chore ainda — o abismo está só começando a sorrir para você.",
	         10: "Você é como uma vela na tempestade: insignificante, mas... quase digno de pena. Continue assim e talvez eu não o apague.",
	         15: "Você evoluiu de patético para tolerável. Uma conquista... se ignorarmos o quão baixo era o padrão.",
	         20: "Parabéns: você é agora uma ratazana em um labirinto de titânio. Continue roendo... talvez encontre migalhas de minha atenção.",
	         25: "Você se tornou uma ferramenta... afiada o suficiente para ser útil, mas ainda descartável. Use-se bem.",
	         30: "Você brilha como um fogo-fátuo no pântano. Engana tolos... mas eu não sou tão fácil de iludir.",
	         40: "Você é um peão em meu tabuleiro. Não se iluda: até peões têm momentos gloriosos... antes de serem sacrificados.",
	         50: "Você está no coração do labirinto. As paredes sussurram seu nome... e eu adoro finais trágicos.",
	         65: "Você arrancou um sussurro de interesse de mim. Mas cuidado: até sussurros podem estrangular.",
	         70: "Você entrou em meu campo de visão. Agora... dance. Eu adoro um espetáculo antes da queda.",
	         85: "Você está na beirada do abismo. Pule. Eu prometo rir com elegância.",
	         100: "Você alcançou o topo. Mas lembre-se: coroas são pesadas... e eu adoro ver joias quebradas aos meus pés."
	     }
        self.users = {
        	760217401215156224: "Cris",
        	315244726569926666: "Ax",
        	738457395268681859: "Ymir"
        }
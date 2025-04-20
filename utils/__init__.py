from .useful_system import UsefulSystem
import os
from easy_pil import Editor, Canvas, Font, load_image_async
import discord
import bisect

class utilsPort:
	def __init__(self):
		self.use = UsefulSystem()
		self.base_path = os.path.dirname(__file__)
        
		self.assets = {
            # Certifique-se de que o nome do arquivo esteja correto.
            # Se o arquivo de fundo não existir, você pode precisar criar ou ajustar o nome.
            'profile_bg': os.path.join(self.base_path,'profile.png'),
            'houses': {
                'Leonipards': os.path.join(self.base_path,'leonipards.png'),
                'Synexa': os.path.join(self.base_path, 'synexa.png'),
                'Corbusier': os.path.join(self.base_path, 'corbusier.png'),
                'Vildjharta': os.path.join(self.base_path, 'vildjharta.png'),
                'cidadao': os.path.join(self.base_path, 'cidadao.png'),
                'imperador': os.path.join(self.base_path,"imperador.png")
                
            }
        }
		self.fonts = {
            'name': Font.poppins(variant="bold", size=25),
            'body': Font.poppins(size=14),
            'rank': Font.poppins(size=20)
        }
		self.users = {
        	315244726569926666: "imperador"
        }
		self.bei_word = [
        	"teste"
        ]
		self.cor = discord.Color.default()
		self.taxa = {
		    range(1, 26): 3,
		    range(26, 51): 7,
		    range(51, 101): 13
		}
		self.intervalos_ordenados = sorted(
		    [(r.start, r.stop, v) for r, v in self.taxa.items()],
		    key=lambda x: x[0]
		)
		self.inicios = [intervalo[0] for intervalo in self.intervalos_ordenados]
		self.fins = [intervalo[1] for intervalo in self.intervalos_ordenados]
		self.valores = [intervalo[2] for intervalo in self.intervalos_ordenados]
		
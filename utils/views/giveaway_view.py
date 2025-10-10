import logging
import discord
from typing import Dict, Tuple, Union
from datetime import datetime, timedelta
from discord import Member, TextChannel
from utils.handlers.dbs_handler import dbs_controller
from utils.handlers.level_handler import LevelHandler
from utils.useful_system import UsefulSystem
from datetime import datetime
import random
import asyncio

logger = logging.getLogger(__name__)
class giveawaycontroller:
    claimed = False
    use = UsefulSystem()
    
    @staticmethod
    def xp_button(xp: int, level: int, interact: discord.Interaction):
        rate = LevelHandler.get_rate(level)
        xp_needed = LevelHandler.xp_required(level, rate)
        levels = 0
        while xp >= xp_needed:
            xp -= xp_needed
            levels +=1
            level +=1
            rate = LevelHandler.get_rate(level)
            xp_needed = LevelHandler.xp_required(level, rate)
        logger.info(f"rastreio do xp (caixa), xp: {xp}")
        data = {
            "levels_gained": levels,
            "xp_remainder": xp,
            "new_level": level,
            "interact": interact
        }
        return data
          
    @staticmethod      
    async def box_check(channel, user_data, box, xp):
          if box < 300:
              logger.info(f"atualmente a caixa tem: {box}")
              logger.info(f"xp atual da caixa: {xp}")
              return None
          giveawaycontroller.claimed = False
          half_xp = int(xp/2)
          xp = random.randint(half_xp, xp)
          loop = asyncio.get_event_loop()
          future = loop.create_future()
          
          async def button_response(interact: discord.Interaction):
              user_id = str(interact.user.id)
              if giveawaycontroller.claimed:
                  return
              
              giveawaycontroller.claimed = True
              botao.disabled = True
              view.clear_items()
              await interact.message.edit(view=view)
              
              rate = LevelHandler.get_rate(user_data["level"])
              xp_needed = LevelHandler.xp_required(user_data["level"], rate)
              user_data["xp"] += xp
              embed = await giveawaycontroller.use.create("Drop", f"A glória é vossa! Os ** {xp} ** pontos de progresso foram adicionados à vossa jornada, aproveite-os {interact.user.mention}!", discord.Color.green())
              await interact.response.send_message(embed=embed)
              if user_data["xp"] >= xp_needed:
                  data = giveawaycontroller.xp_button(user_data["xp"], user_data["level"], interact)
                  
              else:
                  data = {
                      "levels_gained": 0,
                      "xp_remainder": user_data["xp"],
                      "new_level": 0,
                      "interact": interact
                  }
              future.set_result(data)
          
          
          view = discord.ui.View(timeout=10.0)
          botao = discord.ui.Button(label="CLAIM", style = discord.ButtonStyle.green)
          botao.callback = button_response
          view.add_item(botao)
          msg = (
              "Atenção, valorosos membros do Império que estão presentes no chat!\n\n"
              "Uma bênção de experiência foi ativada em vosso favor!"
              f"Preparem-se, pois a glória de ** {xp} ** pontos de xp aguarda.\n\n"
              "Fiquem sabendo: apenas o primeiro a interagir receberá esta dádiva.\n\n"
              "Que o mais rápido seja agraciado!"
          )
          embed = await giveawaycontroller.use.create("**XP liberado!**", msg)
              
          await channel.send(embed=embed, view=view)
          data = await future
          return data
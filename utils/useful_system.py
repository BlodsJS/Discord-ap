import logging
import discord
from typing import Dict, Tuple, Union
from datetime import datetime, timedelta
from discord import Member, TextChannel
import bisect
from datetime import datetime
import pathlib
import json
import random
import locale

logger = logging.getLogger(__name__)

# ************************** UTILITY FUNCTIONS **************************
class UsefulSystem:
    def __init__(self, arquivo: str = 'log.txt'):
        self.cor = discord.Color.default()
        self.arquivo = pathlib.Path(arquivo)
        #locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
        logger.info("Useful carregado")
        self.taxa = {
		    range(1, 26): 20,
		    range(26, 51): 20,
		    range(51, 101): 35
        }
        self.intervalos_ordenados = sorted(
		    [(r.start, r.stop, v) for r, v in self.taxa.items()],
		    key=lambda x: x[0]
		)
        self.inicios = [intervalo[0] for intervalo in self.intervalos_ordenados]
        self.fins = [intervalo[1] for intervalo in self.intervalos_ordenados]
        self.valores = [intervalo[2] for intervalo in self.intervalos_ordenados]
        

    # creates standard embeds
    async def create(self, title, desc, color = None):
        color = self.cor if color is None else color
        embed = discord.Embed(
            title= title,
            description= desc,
            color= color
        )
        logger.info(f"objeto retornado na embed: {embed}")
        return embed

    # get rate based on level
    async def obter_taxa(self, inicios, fins, valores, acount):
        idx = bisect.bisect_right(inicios, acount) - 1
        if idx >= 0 and acount < fins[idx]:
            return valores[idx]
        return 100  # Valor fora dos intervalos

    # logs events, but still under development
    async def log_save(self, texto: str, arquivo: str =  "log.txt"):
        """Registra um evento com timestamp no arquivo especificado."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linha = f"[{timestamp}] {texto}\n"
        with open(arquivo, "a", encoding="utf-8") as f:
            f.write(linha)

    # checks if the user has a specific role 
    async def has_role(self, member, role_id):
        user_role_ids = [role.id for role in member.roles]
        return role_id in user_role_ids

    # get the positions (and xp rates) for verification of; xp gained; position gained
    def get_roles(self):
        file_json = self.arquivo.parent.joinpath("utils/dbs/cargos.json")
        with open(file_json, encoding="utf-8") as f:
            return json.load(f)

    def get_profile(self):
        file_json = self.arquivo.parent.joinpath("utils/dbs/users_profile.json")
        with open(file_json, encoding="utf-8") as f:
            return json.load(f)

    def edit_profile(self, user_id: str, field: str, value: str):
        try:
            file_json = self.arquivo.parent.joinpath("utils/dbs/users_profile.json")
            profiles = self.get_profile()
            if user_id not in profiles:
                profiles[user_id] = {}
            
            if field == "theme":
                banners = self.check_profiles()
                value = banners.get(value)
                if value:
                    profiles[user_id][field] = value
                
            profiles[user_id][field] = value
            with open(file_json, "w", encoding="utf-8") as f:
                json.dump(profiles, f, ensure_ascii=False, indent=4)
        except  Exception as e:
            logger.info(f"Erro na gravação: {e}")


    def check_profiles(self):
        file_json = self.arquivo.parent.joinpath("utils/dbs/standart_banners.json")
        with open(file_json, encoding="utf-8") as f:
            return json.load(f)
          
    # adds a specified role (used in events and by admin users)
    async def add_role(self, member, role_id):
        role = discord.utils.get(member.guild.roles, id= role_id)
        await member.add_roles(role)

    # removes specified roles (used by events and admin users)
    async def remove_role(self, member, role_id):
        role = discord.utils.get(member.guild.roles, id= role_id)
        await member.remove_roles(role)

    async def chang_role_movchat(self, role: Union[discord.Role, int], users: list, guild):
        if isinstance(role, int):
            role = guild.get_role(role)

        message = "Antigos mov chat:\n\n"
        i = 1
        for member in role.members:
            logger.info(f"removendo cargo: {i}")
            sucess = await member.remove_roles(role)
            message += f"{i}. {member.mention}\n"
            i +=1
        
        message += "\nNovos mov chat:\n\n"
        i = 1
        for member in users:
            logger.info("adicionando cargos")
            success = await member.add_roles(role)
            message += f"{i}. {member.mention}\n"
            i+=1

        return message

    async def ranking_chats(self, guild, role):
        acounts = {}
        today = datetime.utcnow()
        initial_month = datetime(today.year, today.month, 1)
        end_month = initial_month.replace(month= initial_month.month +1) - timedelta(seconds=1)
          
        for channel in guild.text_channels:
            logger.info(f"analisando canal: {channel}")
            try:
                async for message in channel.history(limit= None, after=initial_month, oldest_first=True):
                    
                    if not message.author.bot:
                        author_id = message.author.id
                        if author_id not in acounts:
                            acounts[author_id] = {
                                "acount": 0,
                                "name": f"{message.author.mention}",
                            }
                        acounts[author_id]["acount"] += 1
                        
            except  Exception as e:
                logger.info(f"Erro no contador de mensagens, {e}")
        
        sorted_users = sorted(acounts.items(), key=lambda x: x[1]["acount"], reverse=True)
        users = ""
        new_mov = []
        try:
            idx = 0
            for i, (user_id, count) in enumerate(sorted_users, 1):
                if i>11:
                    break
                logger.info(f"construindo ranking, {i}")
                user_obj = guild.get_member(user_id)
                if i < 4:
                    new_mov.append(user_obj)
                emojis = {
                  1: "🥇",
                  2: "🥈",
                  3: "🥉"
                }
                emoji = emojis.get(i, i)
                name = user_obj.mention if user_obj else f"ID:{user_id}"
                users += f"{emoji}. {name}: **{count['acount']:,}** mensagens\n"
                
        except  Exception as e:
            logger.info(f"Erro no ranking, {e}")

        movs = await self.chang_role_movchat(role, new_mov, guild)
        data_mes = today.strftime("%B").capitalize()
        data_today = today.strftime("%d/%m/%Y")
        data_hour = today.strftime("%H:%M")
        
        message= (
            f"🗓️•Referente a **{data_mes}/2025**\n"
            f"🕓•Emitido em: `{data_today} às {data_hour}`\n\n"
            f"{movs}\n\n"
            f"🏆•Ranking:\n\n {users}"
        )
        return message

    async def amplifier_role(self, member):
        taxa_id = None
        roles_to_check = [1378828848657072128, 1378833871306625055]
        for i in roles_to_check:
            if await self.has_role(member, i):
                taxa_id = i
                break
        roles = self.get_roles()
        taxa_role = roles.get(str(taxa_id), 0)
        amplifier = 1
        if taxa_id is not None:
            amplifier +=taxa_role     
        return amplifier

    async def xp_calc(self, level, taxa):
        xp_needed = (level**2)*taxa +100
        return xp_needed

    async def amplifier_calc(self, amount):
        amplifier = 0
        value = int(amount)//5
        if value >= 25:
            amplifier = 4
            return amplifier
        amplifier = 0.2*value
        return amplifier

    async def levling(self, user_data, user):
        taxa = taxa = await self.obter_taxa(self.inicios, self.fins, self.valores, user_data["level"])
        need = await self.xp_calc(user_data["level"], taxa)
        xp = user_data["xp"]
        levels = 0
        
        if xp >= need:
            while xp >= need:
                xp -= need
                levels += 1
                
        

    async def level_check(self, user_data, taxa, user):
        if user_data["xp"] >= (user_data["level"]**2) * taxa +100:
            new_level = user_data["level"] +1
            new_xp = max(user_data["xp"] - ((user_data["level"]**2) * taxa), 0)
            i = None
            level = (new_level//5)*5
            if level > 0: 
                
                roles = self.get_roles()
                role_id = roles.get(str(level))
                i = role_id
                if role_id is None:
                    return
                
                await self.add_role(user, role_id)
                level -= 5
                if level ==0:
                    return
                
                role_id = roles.get(str(level))
                if role_id is None:
                    return
                await self.remove_role(user, role_id)
                return [new_level, new_xp, i]
            return [new_level, new_xp, None]
        else:
            return None

    async def check_role(self, level, user):
        level = (level // 5) * 5
        if level <= 0:
            return
        roles = self.get_roles()
        current_role_id = roles.get(str(level))
        # Obtém o cargo atual correspondente ao level
        if current_role_id is None:
            return
        # Se o usuário já possui o cargo do level atual, não faz nada
        if await self.has_role(user, current_role_id):
            return
        # Adiciona o cargo do nível atual
        await self.add_role(user, current_role_id)
        logger.info(f"[XP] Adicionado cargo de level {level}")
        # Itera sobre todas as chaves, e remove qualquer cargo com level abaixo do atual
        for lvl_str, role_id in roles.items():
            if not lvl_str.isdigit():
                continue  # Pula as entradas que não são níveis
            lvl = int(lvl_str)
            if lvl < level:
                if await self.has_role(user, role_id):
                    try:
                        await self.remove_role(user, role_id)
                        logger.info(f"[XP] Removido cargo antigo de level {lvl}")
                    except Exception as e:
                        logger.warning(f"[XP] Erro ao remover cargo de level {lvl}: {e}")
        return current_role_id
  
          

    async def xp_button(self, xp, level) -> tuple[int, int, int]:
        taxa = await self.obter_taxa(self.inicios, self.fins, self.valores, level)
        xp_need = await self.xp_calc(level, taxa)
        levels = 0
        while xp >= xp_need:
            xp -= xp_need
            levels +=1
            level +=1
            taxa = await self.obter_taxa(self.inicios, self.fins, self.valores, level)
            xp_need = await self.xp_calc(level, taxa)
        logger.info(f"rastreio do xp (caixa), xp: {xp}")
        return levels, xp, level
          
            
    async def box_check(self, channel, user_data, box, db, taxa):
          async def button_response(interact: discord.Interaction):
              user_id = str(interact.user.id)
              if self.claimed:
                  return
              
              self.claimed = True
              botao.disabled = True
              view.clear_items()
              await interact.message.edit(view=view)
              
              taxa = await self.obter_taxa(self.inicios, self.fins, self.valores, user_data["level"])
              xp_need = await self.xp_calc(user_data["level"], taxa)
              user_data["xp"] += xp
              embed = await self.create("Drop", f"A glória é vossa! Os ** {xp} ** pontos de progresso foram adicionados à vossa jornada, aproveite-os {interact.user.mention}!", discord.Color.green())
              
              if user_data["xp"] >= xp_need:
                  gains = await self.xp_button(user_data["xp"], user_data["level"])
                  sucess = await self.check_role(gains[2], interact.user)
                  await db.increment_level(user_id, gains[0])
                  await db.set_field("xp", user_id, gains[1])
                  await interact.response.send_message(embed=embed)
                  return 
                
              await db.increment_xp(user_id, xp)
              
              await interact.response.send_message(embed=embed)
              return
          
          if box >= 300:
              self.claimed = False
              xp = random.randint(100, 600)
              view = discord.ui.View(timeout=10.0)
              botao = discord.ui.Button(label="CLAIM", style = discord.ButtonStyle.green)
              botao.callback = button_response
              view.add_item(botao)
              embed = await self.create("**XP liberado!**", "Atenção, valorosos membros do Império que estão presentes no chat!\n\n"
                                          "Uma bênção de experiência foi ativada em vosso favor!\n"
                                          f"Preparem-se, pois a glória de ** {xp} ** pontos de xp aguarda.\n\n"
                                          "Fiquem sabendo: apenas o primeiro a interagir receberá esta dádiva.\n\n"
                                          "Que o mais rápido seja agraciado!")
              
              await channel.send(embed=embed, view=view)
              return xp
          else:
              logger.info(f"atualmente a caixa tem {box}")
              return None
            
      

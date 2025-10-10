import discord
from discord import Member
from utils.handlers.dbs_handler import dbs_controller

class roles_controller:
    
    @staticmethod
    async def has_role(member, role_id):
        user_role_ids = [role.id for role in member.roles]
        return role_id in user_role_ids
    
    @staticmethod
    async def add_role(member, role_id):
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print(f"Não tenho permissão para adicionar o cargo {role.name} a {member}.")
            except discord.HTTPException:
                print(f"Erro ao tentar adicionar o cargo {role.name} a {member}.")
    
    @staticmethod
    async def remove_role(member, role_id):
        role = discord.utils.get(member.guild.roles, id= role_id)
        await member.remove_roles(role)
        
    @staticmethod
    async def get_roles(member: Member):
        return member.roles
    
    @staticmethod
    async def check_role(level, member: Member):
        new_level= (level//5)*5
        if new_level > 0:
            roles = dbs_controler.load_roles("roles")
            role_id = roles.get(str(new_level))
            i = role_id
            if role_id is None:
                return
                
            await roles_controller.add_role(member, role_id)
            logger.info(f"cargo adicionado com sucesso, id: {role_id}")
            new_level -= 5
            if level ==0:   
                return role_id
                
            role_id = roles.get(str(new_level))
            if role_id is None:
                return i
            await roles_controller.remove_role(member, role_id)
            logger.info(f"cargo removido com sucesso, id: {role_id}")
            return i
        else:
            return None
    
      
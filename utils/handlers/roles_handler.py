import discord

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
    
    
    
      
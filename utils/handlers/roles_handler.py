import discord

class roles_controler:
    
    @staticmethod
    async def add_role(member: discord.Member, role_id: int):
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role, reason="Automação do sistema de testes")
            except discord.Forbidden:
                print(f"Não tenho permissão para adicionar o cargo {role.name} a {member}.")
            except discord.HTTPException:
                print(f"Erro ao tentar adicionar o cargo {role.name} a {member}.")
# admin/__init__.py
import discord
from .admin_roles import admin_role_commands
from .admin_channels import admin_channel_commands
from .admin_levels import admin_level_commands
from .admin_economy import admin_economy_commands
from .admin_configs import admin_config_commands
from .admin_users import admin_user_commands
#carregamento dos comandos de administração 

async def setup(bot):
    bot.add_cog(admin_role_commands(bot))
    bot.add_cog(admin_channel_commands(bot))
    bot.add_cog(admin_level_commands(bot))
    bot.add_cog(admin_economy_commands(bot))
    bot.add_cog(admin_config_commands(bot))
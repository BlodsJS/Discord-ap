from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
from utils.views.config_view import ConfigView
import re
import logging

class admin_config_commands(BaseCommands):
    
    @commands.command(name="configurações", aliases=["config"])
    @commands.has_permissions(administrator=True)
    async def configs_prefix(self, ctx):
        try:
            configs = self.dbs_controler.load_all_configs()
            translater = self.dbs_controler.load_translater()
            configs_view = ConfigView()
            embed = await self.use.create(
                "**painel de condifuração:**",
                "Principais sistemas do bot, cuidado ao mexer!!\n\nClique no botão para ver as demais configurações desse sistema."
            )
            await ctx.channel.send(embed=embed, view=configs_view)
        except Exception as e:
            print(e)
from cogs.commands import BaseCommands
import discord
import typing
from typing import Union
from discord.ext import commands
from discord import app_commands, Member, TextChannel, VoiceChannel
import re
import logging

class admin_badges_commands(BaseCommands):
    @commands.command(name="createbadge")
    async def create_badge_prefix(self, ctx, name, file, des=" "):
        if not name or file:
            return
        badges = self.db_controler.load_all_configs()
        
        new_badge = {
            "name": name,
            "file": file,
            "description": des
        }
        
        badges["badges"][name] = new_badge
        self.db_controler._save(self.db_controler.all_configs_file, data)
        embed = await self.use.create("Sucess", f"Medalha criada e adicionada ao codex")
        await ctx.send(embed=embed)
    
    @commands.command(name="removebadge")
    async def remove_badge_prefix(self, ctx, member: Member, name):
        try:
            users = self.db_controler.load_profiles()
            user_data = users.get(str(member.id), {})
            if "badges" not in user_data or name not in user_data["badges"]:
                embed = await self.use.create("erro", "O usuário não tem essa medalha")
                await ctx.send(embed=embed)
                return
            user_data["badges"].remove(name)
            users[str(member.id)] = user_data
            self.db_controler._save(self.db_controler.profiles_file, users)
            embed = await self.use.create("Sucess", f"Medalha removida de {member.mention}")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
    
    @commands.command(name="addbadge")
    async def add_badge_prefix(self, ctx, member:Member, name):
        badges = self.db_controler.load_all_configs()
        badge = badges["badges"].get(name)
        if badge == None:
            embed = await self.use.create("erro", "Essa medalha não existe ")
            await ctx.send(embed=embed)
            return
        users = self.db_controler.load_profiles()
        user_data = users.get(str(member.id), {})
        if name in user_data["badges"]:
            embed = await self.use.create("erro", "O usuário já tem essa medalha ")
            await ctx.send(embed=embed)
        
        user_data["badges"].append(name)
        users[str(member.id)] = user_data
        self.db_controler._save(self.db_controler.profiles_file, users)
        embed = await self.use.create("Sucess", f"Medalha concedida a {member.mention}")
        await ctx.send(embed=embed)
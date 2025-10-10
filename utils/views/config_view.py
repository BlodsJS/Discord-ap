import discord
from utils.handlers.dbs_handler import dbs_controller
from utils.handlers.roles_handler import roles_controller
import json
from pathlib import Path

class ConfigView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.all_configs = dbs_controller.load_all_configs()

        for key in self.all_configs:
            button = discord.ui.Button(
                label=key.capitalize(),
                style=discord.ButtonStyle.green,
                custom_id=f"config_opcao_{key}"
            )
            button.callback = self.make_callback(key)
            self.add_item(button)

    def make_callback(self, key: str):
        async def callback(interaction: discord.Interaction):
            value = self.all_configs[key]
            if isinstance(value, dict):
                # gera nova view com subopções
                view = discord.ui.View()
                msg = ""
                for sub_key, sub_value in value.items():
                    btn = discord.ui.Button(label=sub_key.capitalize(), style=discord.ButtonStyle.blurple)
                    msg += f"**{sub_value}**\n"
                    async def sub_callback(inter, v=sub_value):
                        if isinstance(v, dict):
                            # aqui poderia continuar descendo
                            
                            await inter.response.send_message(f"Subnível {v}", ephemeral=True)
                            
                        else:
                            # fim
                            await inter.response.send_message(f"Valor final: {v}", ephemeral=True)
                    btn.callback = sub_callback
                    view.add_item(btn)

                # botão voltar
                back = discord.ui.Button(label="Voltar", style=discord.ButtonStyle.red)
                async def back_callback(inter):
                    embed = discord.Embed(
                      title="Configurações principais:",
                      description="Principais sistemas do bot, cuidado ao mexer!!\n\nClique no botão para ver as demais configurações desse sistema."
                    )
                    await inter.response.edit_message(embed=embed, view=ConfigView())
                back.callback = back_callback
                view.add_item(back)
                embed = discord.Embed(
                  title=key,
                  description=f"Aqui ficaram as configurações que podem ser alteradas dessa categoria!!\n\n{msg} "
                )

                await interaction.response.edit_message(embed=embed, view=view)
            else:
                await interaction.response.send_message(f"Valor final: {value}", ephemeral=True)

        return callback
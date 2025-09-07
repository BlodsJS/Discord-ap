# utils/views/house_view.py
import discord
from utils.handlers.house_handler import TestHandler
from utils.handlers.dbs_handler import dbs_controler
from utils.handlers.roles_handler import roles_controler
import json
from pathlib import Path

class TestView(discord.ui.View):
    def __init__(self, question_data: dict, thread_id: int, user_id: int):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.question_data = question_data
        self.user_id = user_id
        self.current_index = -1
        self.questions = self.load_questions()
        self.houses = self.load_map()

        options = ['A', 'B', 'C', 'D']
        for option in options:
            button = discord.ui.Button(
                label=option,
                style=discord.ButtonStyle.green,
                custom_id=f"test_opcao_{option.lower()}_{thread_id}"
            )
            button.callback = self.make_callback(option)
            self.add_item(button)

        cancel = discord.ui.Button(
            label="Cancelar",
            style=discord.ButtonStyle.red,
            custom_id=f"test_cancelar_{thread_id}"
        )
        cancel.callback = self.cancel_callback
        self.add_item(cancel)

    def load_questions(self):
        QUESTIONS_FILE = Path("utils/dbs/questions.json")
        if not QUESTIONS_FILE.exists():
            return []
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_map(self):
        map_file = Path("utils/dbs/map.json")
        with open(map_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def make_callback(self, option: str):
        async def callback(interaction: discord.Interaction):
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("Este teste não é seu.", ephemeral=True)
                return

            # delega a resposta ao handler
            await TestHandler.register_answer(
                thread_id=self.thread_id,
                user_id=self.user_id,
                question=f"q{self.current_index +1}",
                answer=option
            )
            self.current_index +=1
            if self.current_index < len(self.questions):
                # Edita apenas o embed, a view permanece a mesma
                q = self.questions[self.current_index]
                text = (f"{q['text']}\n\n"
                        f"A - {q['options'][0]}\n"
                        f"B - {q['options'][1]}\n"
                        f"C - {q['options'][2]}\n"
                        f"D - {q['options'][3]}\n"
                       )
                embed = discord.Embed(
                    title=f"**Questão {self.current_index + 1}**",
                    description=text
                )
                await interaction.response.edit_message(embed=embed)
            else:
                # Última pergunta: finaliza
                text = "Confira suas respostas\n\n"
                data = TestHandler.load_data()
                user_data = data[str(self.user_id)][str(self.thread_id)]
                
                results = await self.verify_house(user_data)
                winners, votes, house_ids = await self.verify_winners(results)
                
                
                embed = discord.Embed(
                    title= "✨ Teste concluído!",
                    description=f"Você tem {votes} votos e as casas vencedoras são: {', '.join(winners)}"
                )
                await interaction.response.edit_message(embed=embed, view=None)
                await self.send_house_buttons_simple(interaction, winners, house_ids)
            #await interaction.response.send_message(f"Você escolheu **{option}**!", ephemeral=True)

        return callback

    async def cancel_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Teste cancelado.", ephemeral=True)
        self.stop()
        TestHandler.clear_user(interaction.user.id)
        thread = interaction.guild.get_thread(self.thread_id)
        await thread.delete()
        
    
    async def verify_house(self, answers):
        
        results = {
            "Leonipards": 0,
            "Corbusier": 0,
            "Vildjharta": 0,
            "Synexa": 0
        }
        for key, value in answers.items():
            if key == "q0":  # pula a primeira pergunta
                continue
            house = self.houses[key][value]
            results[house] += 1
        return results  # votos por casa
    
    async def verify_winners(self, results):
        houses_data = dbs_controler.load_house("houses")  # pega todos os IDs do JSON
        max_votes = max(results.values())
        winners = [house for house, points in results.items() if points == max_votes]
        # sempre retorna uma lista de casas vencedoras e IDs correspondentes
        winner_ids = [houses_data[w] for w in winners]
        return winners, max_votes, winner_ids

    async def send_house_buttons_simple(self, interaction: discord.Interaction, winners: list[str], house_ids: list[int]):
        """Cria botões simples para as casas vencedoras e envia na thread."""
        view = discord.ui.View(timeout=None)
        for house_name, role_id in zip(winners, house_ids):
            button = discord.ui.Button(label=house_name, style=discord.ButtonStyle.green)
            async def button_callback(interaction: discord.Interaction, role_id=role_id):
                member = interaction.guild.get_member(interaction.user.id)
                await roles_controler.add_role(member, role_id)
                await interaction.response.send_message(
                  f"{member.mention}, você agora pertence à casa {house_name}!", ephemeral=True
                )
                thread = interaction.guild.get_thread(self.thread_id)
                await thread.delete()
            button.callback = button_callback
            view.add_item(button)
        await interaction.channel.send("Escolha sua casa vencedora:", view=view)

        
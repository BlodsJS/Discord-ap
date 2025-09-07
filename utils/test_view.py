# utils/views/test_view.py

import discord

class TestView(discord.ui.View):
    def __init__(self, question_data: dict, thread_id: int):
        super().__init__(timeout=None)
        self.thread_id = thread_id
        self.question_data = question_data

        options = ['A', 'B', 'C', 'D']
        for i, option in enumerate(options):
            label = option
            custom_id = f"test_opcao_{option.lower()}_{thread_id}"
            self.add_item(discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.green,
                custom_id=custom_id
            ))

        self.add_item(discord.ui.Button(
            label="Cancelar",
            style=discord.ButtonStyle.red,
            custom_id=f"test_cancelar_{thread_id}"
        ))
      
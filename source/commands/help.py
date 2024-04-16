from discord.ui import View, button, Button
from discord import Embed, Message
from command import Command

import discord


class Select(discord.ui.Select):
    def __init__(self, callback_function):
        import bot 
        self.callback_function = callback_function
        options = list()
        for command in bot.commands:
            options.append(discord.SelectOption(label=command.command_name, description=command.description))
        super().__init__(placeholder="Select an option",max_values=1,min_values=1,options=options)
    
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.callback_function(self.values[0])

class SelectView(discord.ui.View):
    def __init__(self, *, timeout = 180):
        super().__init__(timeout=timeout)
        self.add_item(Select(self.callback_function))

    async def callback_function(self, command_name):
        import bot# Avoid circular import...
        for command in bot.commands:
            if command.command_name == command_name:
                await self.message.edit(embed=discord.Embed(title=f"{command.command_name}", description=f"Aliases: {', '.join(command.triggers)}\n{command.description}\n{command.help}"))
                return
    
    async def reply(self, message: Message):
        import bot # Avoid circular import...
        content = ""
        for command in bot.commands:
            content += f"{command.command_name} | {command.description}\n"
        self.message = await message.reply(embed=Embed(title="Help", description=content), view=self)
    
class HelpCommand(Command):
    
    def __init__(self) -> None:
        super().__init__('help', 'Get help')

    async def run(self, message: discord.Message, args: list[str], parsed: dict[str, str]):
        await SelectView().reply(message)
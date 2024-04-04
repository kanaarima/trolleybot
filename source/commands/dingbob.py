from command import Command
import discord

class Dingbob(Command):
    def __init__(self):
        super().__init__('dingbob', 'Dingbob')

    async def run(self, message: discord.Message, args: list[str]):
        return await message.reply('bobding')
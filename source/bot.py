import traceback
from commands.search_1s import SearchUser1s, SearchClan1s
from commands.yoruba_quotes import YorubaQuotesCommand
from commands.user_info import UserInfo, UserSkills, GenerateTopPlaysCollection
from commands.debug import TestSkill
from commands.simulate import Simulate
from commands.help import HelpCommand

import discord
import config
import shlex

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
commands = [UserInfo(), SearchUser1s(), SearchClan1s(), YorubaQuotesCommand(), TestSkill(), UserSkills(), GenerateTopPlaysCollection(), HelpCommand(), Simulate()]

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if message.content.startswith('t!'):
        split = shlex.split(message.content)
        trigger = split[0][2:]
        args = split[1:]
        for command in commands:
            if command.is_me(trigger):
                try:
                    await command.run(message, args, command.parse_args(args))
                except Exception as e:
                    embed = discord.Embed(title=f"An error occurred! ({e.__class__.__name__})", color=discord.Color.red())
                    embed.description = f"{str(e)}\n```py\n{traceback.format_exc()}\n```"
                    await message.reply(embed=embed)
                return
        await message.reply("Command not found!")
    else:
        if len(message.content) > 200:
            await message.reply(f"https://tenor.com/view/adachi-persona-persona4-ultimax-talk-gif-25156593")
            return
        if 'needs to do something' in message.content.lower():
            await message.reply(f'<:adachitrue:1222126444444909598>')

if __name__ == '__main__':
    client.run(config.DISCORD_BOT_TOKEN)

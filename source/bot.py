from commands.search_1s import SearchUser1s, SearchClan1s
from commands.yoruba_quotes import YorubaQuotesCommand
from commands.user_info import UserInfo

import discord
import config
import shlex

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
commands = [UserInfo(), SearchUser1s(), SearchClan1s(), YorubaQuotesCommand()]

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
                await command.run(message, args, command.parse_args(args))
                return
        await message.reply("Command not found!")
    else:
        if len(message.content) > 200:
            await message.reply(f"https://tenor.com/view/adachi-persona-persona4-ultimax-talk-gif-25156593")
            return
        if 'needs to do something' in message.content.lower():
            await message.reply(f'<:adachitrue:1222126444444909598>')

client.run(config.DISCORD_BOT_TOKEN)

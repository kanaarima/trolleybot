from commands.dingbob import Dingbob

import discord
import config
import shlex

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
commands = [Dingbob()]

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if 'needs to do something' in message.content.lower():
        await message.reply(f'<:adachitrue:1222126444444909598>')
        return
    if message.content.startswith('t!'):
        split = shlex.split(message.content)
        trigger = split[0][2:]
        args = split[1:]
        for command in commands:
            if command.is_me(trigger):
                await command.run(message, args)
                return
        await message.reply("Command not found!")

client.run(config.DISCORD_BOT_TOKEN)

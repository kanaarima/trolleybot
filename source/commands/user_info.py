from api.akatsuki import instance
from command import Command
import discord
import random

class UserInfo(Command):
    def __init__(self) -> None:
        super().__init__('user_info', 'Get information about a user')

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0:
            await message.reply("Please specify an user")
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        user_id = instance.lookup_user(parsed['default'][0])
        if user_id == -1:
            await message.reply("User not found")
            return
        user = instance.get_user_stats(user_id)
        stats = user.stats[relax]
        stats = stats[[*stats.keys()][mode]]
        first_places_count = instance.get_user_first_places(user_id, mode, relax, True)[1]
        embed = discord.Embed(title=f"User info for {user.username}", color=discord.Color.red())
        embed.add_field(name="Registered", value=user.registered_on.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Last seen", value=user.latest_activity.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Rank", value=f"#{stats.global_leaderboard_rank} (#{stats.country_leaderboard_rank} {user.country})", inline=True)
        embed.add_field(name="PP", value=f"{stats.pp}pp", inline=True)
        embed.add_field(name="First Places", value=f"{first_places_count}", inline=True)
        embed.set_thumbnail(url=f"https://a.akatsuki.gg/{user_id}?{random.randint(0, 1000000)}")
        await message.reply(embed=embed)
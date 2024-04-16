import io
from api.akatsuki import instance
from command import Command
import collection
import discord
import random
import pp

class UserInfo(Command):
    def __init__(self) -> None:
        super().__init__('user_info', 'Get information about a user')
        self.help = """
        Arguments: <username/userid> <-mode>
        Modes: std/std_rx/std_ap/taiko/taiko_rx/ctb/ctb_rx/mania
        """

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0:
            await message.reply("Please specify an user")
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        if parsed["default"][0].isnumeric():
            user_id = int(parsed["default"][0])
        else:
            user_id = instance.lookup_user(parsed['default'][0])
            if user_id == -1:
                await message.reply("User not found")
                return
        user = instance.get_user_stats(user_id)
        if user is None:
            embed = discord.Embed(title=f"User info for restricted user", color=discord.Color.red())
            first_places_count = instance.get_user_first_places(user_id, mode, relax, True)[1]
            if first_places_count == 0:
                await message.reply("User not found!")
                return
            embed.add_field(name="First Places", value=f"{first_places_count}", inline=True)
            embed.set_thumbnail(url=f"https://a.akatsuki.gg/{user_id}?{random.randint(0, 1000000)}")
            await message.reply(embed=embed)
        else:
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

class UserSkills(Command):
    
    def __init__(self) -> None:
        super().__init__('user_skills', 'Get skills of a user')

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
        top_200 = instance.get_user_best(user_id, mode, relax, 1)+instance.get_user_best(user_id, mode, relax, 2)
        aim = list()
        speed = list()
        precision = list()
        acc = list()
        ar = list()
        cs = list()
        for score in top_200:
            attrs = pp.calc_attributes(score.beatmap.beatmap_id, mode, score.mods, score.accuracy, score.count_300, score.count_100, score.count_50, score.count_miss)
            aim.append(attrs.aim_pp)
            if attrs.acc_pp < 0:
                speed.append(attrs.speed_pp+attrs.acc_pp)
            else:
                speed.append(attrs.speed_pp)
                acc.append(attrs.acc_pp)
            
            precision.append(attrs.aim_pp * (attrs.cs/7.5))
            ar.append(attrs.ar)
            cs.append(attrs.cs)
        aim.sort(key=lambda x: x, reverse=True)
        speed.sort(key=lambda x: x, reverse=True)
        acc.sort(key=lambda x: x, reverse=True)
        ar.sort(key=lambda x: x, reverse=True)
        cs.sort(key=lambda x: x, reverse=True)
        embed = discord.Embed(title=f"User skills for {user.username}", color=discord.Color.red())
        embed.add_field(name="Aim", value=f"{sum(aim[:10])/len(aim[:10]):.2f}", inline=True)
        embed.add_field(name="Speed", value=f"{sum(speed[:10])/len(speed[:10]):.2f}", inline=True)
        embed.add_field(name="Accuracy", value=f"{sum(acc[:10])/len(acc[:10]):.2f}", inline=True)
        embed.add_field(name="Precision", value=f"{sum(precision[:10])/len(precision[:10]):.2f}", inline=False)
        embed.add_field(name="Most comfortable AR", value=f"{sum(ar)/len(ar):.2f}", inline=False)
        embed.add_field(name="Most comfortable CS", value=f"{sum(cs)/len(cs):.2f}", inline=False)
        embed.set_thumbnail(url=f"https://a.akatsuki.gg/{user_id}?{random.randint(0, 1000000)}")
        await message.reply(embed=embed)

class GenerateTopPlaysCollection(Command):

    def __init__(self) -> None:
        super().__init__('top_plays_collection', 'Generate a collection of top plays')
        self.help = """
        Arguments: <username/userid> (-pages N) (-mode)
        Modes: std/std_rx/std_ap/taiko/taiko_rx/ctb/ctb_rx/mania
        N: number of pages (default 1, 1 page = 100 scores)
        """

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0:
            await message.reply("Please specify an user")
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        if parsed['default'][0].isnumeric():
            user_id = int(parsed['default'][0])
        else:
            user_id = instance.lookup_user(parsed['default'][0])
        if user_id == -1:
            await message.reply("User not found")
            return

        pages = 1
        if 'pages' in parsed:
            pages = int(parsed['pages'])
        await message.reply("Generating collection....")
        
        scores = list()
        for page in range(pages):
            scores += instance.get_user_best(user_id, mode, relax, page+1)
        scores = sorted(scores, key=lambda x: x.pp, reverse=True)
        file = collection.generate_collection_from_list(scores, f"{user_id} top plays")
        try:
            await message.reply(file=discord.File(fp=io.BytesIO(file), filename="top_plays.osdb"))
        except Exception as e:
            print(e)
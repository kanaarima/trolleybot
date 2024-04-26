import io
from api.akatsuki import instance, Score
from command import Command

from discord.ui import View, button, Button
from mods import Mods
import discord
import cache
import collection
from utils import MapStats
import time

class FirstPlacesView(View):
    
    def __init__(self, title: str, first_places: list[Score]) -> None:
        super().__init__()
        self.title = title
        self.first_places = first_places
        self.page = 0
        self.desc = True
        self.current_sort = 0
        self.length = 0
        for first_place in first_places:
            if first_place.actual_beatmap:
                length = first_place.actual_beatmap.hit_length
            else:
                length = first_place.beatmap.hit_length
            if first_place.mods & 64:
                self.length += length / 1.5
            else:
                self.length += length / 1.5
        self.sort_methods = ['pp', 'mods', 'rank', 'accuracy', 'max_combo', 'hit length', 'time']
        self.sort(self.sort_methods[self.current_sort], self.desc)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"{self.title} | Page {self.page+1}/{int(len(self.first_places)/7)+1} ({len(self.first_places)}) ({self.length/60/60:.2f} hours)", color=discord.Color.red())
        #embed.description = "```"
        embed.description = ""
        for score in self.first_places[int(self.page*7):int((self.page+1)*7)]:
            title = f"__**{score.beatmap.song_name}**__"
            desc = f"[{score.count_300}/{score.count_100}/{score.count_50}/{score.count_miss}] {score.max_combo}x/{score.beatmap.max_combo}x {score.pp}pp {score.rank} {score.accuracy:.2f}% +{Mods(score.mods).short}"
            if getattr(score, 'actual_beatmap', None) is not None:
                map_stats = MapStats(score.mods, score.actual_beatmap.ar, score.actual_beatmap.od, score.actual_beatmap.hp, score.actual_beatmap.cs, score.actual_beatmap.bpm)
                if score.mods & 64:
                    length = score.actual_beatmap.hit_length/1.5
                else:
                    length = score.actual_beatmap.hit_length
                desc += f"\n**Length**: {length:.1f}s **BPM**: {map_stats.bpm:.0f} **AR**: {map_stats.ar:.1f} **OD**: {map_stats.od:.1f} **CS**: {map_stats.cs:.1f}"
            else:
                desc += f"\nCould not get beatmap info (Deleted set?)"
            desc += f"\n Set on: {score.time.strftime('%Y-%m-%d %H:%M:%S')} [Direct](https://kanaarima.github.io/osu/osudl.html?beatmap={score.beatmap.beatmap_id}) [Bancho](https://osu.ppy.sh/b/{score.beatmap.beatmap_id}) [Akatsuki](https://akatsuki.gg/b/{score.beatmap.beatmap_id})"
            embed.description += f"{title}\n{desc}\n"
        return embed

    @button(label="Previous", style=discord.ButtonStyle.gray)
    async def prev_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @button(label="Next", style=discord.ButtonStyle.gray)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < int(len(self.first_places)/7):
            self.page += 1
            await interaction.response.edit_message(embed=self.get_embed(), view=self)
    
    @button(label="Sort: pp", style=discord.ButtonStyle.gray)
    async def sort_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_sort += 1
        if self.current_sort >= len(self.sort_methods):
            self.current_sort = 0
        button.label = f"Sort: {self.sort_methods[self.current_sort]}"
        self.sort(self.sort_methods[self.current_sort], self.desc)
        await interaction.response.defer()
        await interaction.message.edit(embed=self.get_embed(), view=self)
    
    @button(label="Order: ↓", style=discord.ButtonStyle.gray)
    async def desc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()   
        if self.desc:
            self.desc = False
            button.label = "Order: ↑"
        else:
            self.desc = True
            button.label = "Order: ↓"
        self.sort(self.sort_methods[self.current_sort], self.desc)
        await interaction.message.edit(embed=self.get_embed(), view=self)

    @button(label="Download as CSV", style=discord.ButtonStyle.green)
    async def download_csv(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        csv = "beatmap_id,count_300,count_100,count_50,count_miss,max_combo,pp,rank,accuracy,mods,hit_length,time,title,link\n"
        for score in self.first_places:
            csv += f"{score.beatmap.beatmap_id},{score.count_300},{score.count_100},{score.count_50},{score.count_miss},{score.max_combo},{score.pp},{score.rank},{score.accuracy},{Mods(score.mods).short},{score.beatmap.hit_length},{score.time},{score.beatmap.song_name},https://osu.ppy.sh/b/{score.beatmap.beatmap_id}\n"
        try:
            await interaction.message.reply(file=discord.File(fp=io.BytesIO(csv.encode("utf-8")), filename="first_places.csv"))
        except Exception as e:
            print(e)
    
    @button(label="Download as osdb", style=discord.ButtonStyle.blurple)
    async def download_osdb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        file = collection.generate_collection_from_list(self.first_places, "First Places")
        try:
            await interaction.message.reply(file=discord.File(fp=io.BytesIO(file), filename="first_places.osdb"))
        except Exception as e:
            print(e)
    
    def sort(self, sort_method: str, desc: bool):
        if sort_method == 'hit length':
            self.first_places.sort(key=lambda x: x.actual_beatmap.hit_length if x.actual_beatmap else x.beatmap.hit_length, reverse=desc)
        else:
            self.first_places.sort(key=lambda x: getattr(x, sort_method), reverse=desc)

    async def reply(self, message: discord.Message):
        embed = self.get_embed()
        await message.reply(embed=embed, view=self)

async def filter_1s(message: discord.Message, first_places: list[Score], parsed: dict[str, str]) -> list[Score]:
        attributes_scores = []
        attributes_beatmap = []

        blacklisted_attributes = ['completed', 'mods', 'play_mode', 'actual_beatmap']
        for k,v in first_places[0].__dict__.items():
            if k in blacklisted_attributes:
                continue
            if type(v) == int or type(v) == float:
                attributes_scores.append(k)

        for k,v in first_places[0].actual_beatmap.__dict__.items():
            if k in blacklisted_attributes:
                continue
            if type(v) == int or type(v) == float:
                attributes_beatmap.append(k)
        
        attributes_special = ['has_mods', 'exclude_mods', 'not_3mod_ss']

        async def warn_invalid_attribute():
            await message.reply(f"Invalid attribute! Valid attributes: {', '.join(attributes_scores+attributes_beatmap+attributes_special)}")

        for key in parsed.keys():
            if key.startswith("min_"):
                attribute = key[4:]
                if attribute in attributes_scores:
                    min_val = float(parsed[key])
                    new_firsts = []
                    for score in first_places:
                        if getattr(score, attribute) >= min_val:
                            new_firsts.append(score)
                    first_places = new_firsts
                elif attribute in attributes_beatmap:
                    min_val = float(parsed[key])
                    new_firsts = []
                    for score in first_places:
                        if score.actual_beatmap:
                            if getattr(score.actual_beatmap, attribute) >= min_val:
                                new_firsts.append(score)
                    first_places = new_firsts
                else:
                    await warn_invalid_attribute()
                    return
            if key.startswith("max_"):
                attribute = key[4:]
                if attribute in attributes_scores:
                    max_val = float(parsed[key])
                    new_firsts = []
                    for score in first_places:
                        if getattr(score, attribute) <= max_val:
                            new_firsts.append(score)
                    first_places = new_firsts
                elif attribute in attributes_beatmap:
                    max_val = float(parsed[key])
                    new_firsts = []
                    for score in first_places:
                        if score.actual_beatmap:
                            if getattr(score.actual_beatmap, attribute) <= max_val:
                                new_firsts.append(score)
                    first_places = new_firsts
                else:
                    await warn_invalid_attribute()
                    return
            
        if 'has_mods' in parsed:
            new_firsts = []
            mods = Mods.from_string(parsed['has_mods'])
            for score in first_places:
                score_mods = Mods(score.mods)
                bad = False
                for mod in mods.members:
                    if mod not in score_mods.members:
                        bad = True
                        break
                if not bad:
                    new_firsts.append(score)
            first_places = new_firsts
        if 'exclude_mods' in parsed:
            new_firsts = []
            mods = Mods.from_string(parsed['exclude_mods'])
            for score in first_places:
                score_mods = Mods(score.mods)
                bad = False
                for mod in mods.members:
                    if mod in score_mods.members:
                        bad = True
                        break
                if not bad:
                    new_firsts.append(score)
            first_places = new_firsts
        if 'not_3mod_ss' in parsed:
            new_firsts = []
            to_exclude = Mods.from_string("HDDTHR")
            for score in first_places:
                mods = Mods(score.mods)
                is_3mod = True
                for mod in to_exclude.members:
                    if mod not in mods.members:
                        new_firsts.append(score)
                        is_3mod = False
                        break
                if not is_3mod:
                    continue
                if score.accuracy < 100:
                    new_firsts.append(score)
            first_places = new_firsts
        return first_places
    
class SearchUser1s(Command):
    
    def __init__(self) -> None:
        super().__init__('searchuser1s', 'Search 1s')
        self.help = """
        Arguments: <username/userid> <-mode> (Filters)
        Modes: std/std_rx/std_ap/taiko/taiko_rx/ctb/ctb_rx/mania
        
        **Available filters**:
        Mod filters: has_mods, exclude_mods, not_3mod_ss (ex. -has_mods DT)
        **General parameters**: 
        count_300, count_100, count_50, count_geki, count_katu, count_miss
        score, max_combo, accuracy, pp
        hit_length, total_length, bpm, ar, od, cs, hp
        beatmap_id, beatmapset_id
        **Example: t!searchuser1s Adachi -min_score 1000 -max_accuracy 99 -std_rx**
        """

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0:
            await message.reply("Please specify an user")
            return
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
        await message.reply(f"Fetching first places...")

        first_places = cache.lookup_first_places(user_id, mode, relax)
        if len(first_places) == 0:
            await message.reply("No first places found!")
            return
        first_places = await filter_1s(message, first_places, parsed)
        if not first_places:
            await message.reply(f"No first places found for {user_id}!")
            return
        await FirstPlacesView(f"First places for {user_id}", first_places).reply(message)

class SearchClan1s(Command):
    
    def __init__(self) -> None:
        super().__init__('searchclan1s', 'Search clan 1s')
        self.help = """
        Arguments: <clan_id> <-mode> (Filters)
        Modes: std/std_rx/std_ap/taiko/taiko_rx/ctb/ctb_rx/mania
        
        **Available filters**:
        Mod filters: has_mods, exclude_mods, not_3mod_ss (ex. -has_mods DT)
        **General parameters**: 
        count_300, count_100, count_50, count_geki, count_katu, count_miss
        score, max_combo, accuracy, pp
        hit_length, total_length, bpm, ar, od, cs, hp
        beatmap_id, beatmapset_id
        **Example: t!searchclan1s 6977 -min_score 1000 -max_accuracy 99 -std_rx**
        """

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0:
            await message.reply("Please specify a clan id")
            return
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        try:
            clan_id = int(parsed['default'][0])
            members = instance.get_clan_members(clan_id)
        except ValueError:
            await message.reply("Invalid clan id")
            return
        except Exception as e:
            print(e)
            await message.reply("Error fetching clan info!")
        await message.reply(f"Fetching first places...")
        to_exclude = list()
        if 'exclude_members' in parsed:
            for member in parsed['exclude_members'].split(","):
                if member.isnumeric():
                    to_exclude.append(int(member))
                else:
                    to_exclude.append(instance.lookup_user(member))
        first_places = list()
        for member in members:
            if member in to_exclude:
                continue
            first_places += cache.lookup_first_places(member, mode, relax)

        if len(first_places) == 0:
            await message.reply("No first places found!")
            return
        first_places = await filter_1s(message, first_places, parsed)
        if not first_places:
            return

        await FirstPlacesView(f"First places for clan {clan_id}", first_places).reply(message)

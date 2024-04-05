import io
from api.akatsuki import instance, Score
from command import Command

from discord.ui import View, button, Button
from mods import Mods
import discord
import cache

class FirstPlacesView(View):
    
    def __init__(self, title: str, first_places: list[Score]) -> None:
        super().__init__()
        self.title = title
        self.first_places = first_places
        self.page = 0
        self.desc = True
        self.current_sort = 0
        self.sort_methods = ['pp', 'mods', 'rank', 'accuracy', 'max_combo', 'hit length', 'time']
        self.sort(self.sort_methods[self.current_sort], self.desc)

    def get_embed(self) -> discord.Embed:
        embed = discord.Embed(title=f"{self.title} | Page {self.page+1}/{int(len(self.first_places)/7)+1} ({len(self.first_places)})", color=discord.Color.red())
        #embed.description = "```"
        embed.description = ""
        for score in self.first_places[int(self.page*7):int((self.page+1)*7)]:
            title = f"**{score.beatmap.song_name}**"
            desc = f"[{score.count_300}/{score.count_100}/{score.count_50}/{score.count_miss}] {score.max_combo}x/{score.beatmap.max_combo}x {score.pp}pp {score.rank} {score.accuracy:.2f}% +{Mods(score.mods).short} \nSet on: {score.time.strftime('%Y-%m-%d %H:%M:%S')}"
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
            csv += f"{score.beatmap.beatmap_id},{score.count_300},{score.count_100},{score.count_50},{score.count_miss},{score.max_combo},{score.pp},{score.rank},{score.accuracy},{score.mods},{score.beatmap.hit_length},{score.time},{score.beatmap.song_name},https://osu.ppy.sh/b/{score.beatmap.beatmap_id}\n"
        try:
            await interaction.message.reply(file=discord.File(fp=io.BytesIO(csv.encode("utf-8")), filename="first_places.csv"))
        except Exception as e:
            print(e)
    
    @button(label="Download as osdb", style=discord.ButtonStyle.blurple)
    async def download_osdb(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
    
    def sort(self, sort_method: str, desc: bool):
        if sort_method == 'hit length':
            self.first_places.sort(key=lambda x: x.beatmap.hit_length, reverse=desc)
        else:
            self.first_places.sort(key=lambda x: getattr(x, sort_method), reverse=desc)

    async def reply(self, message: discord.Message):
        embed = self.get_embed()
        await message.reply(embed=embed, view=self)

class SearchUser1s(Command):
    
    def __init__(self) -> None:
        super().__init__('searchuser1s', 'Search 1s')

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0:
            await message.reply("Please specify an user")
            return
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        user_id = instance.lookup_user(parsed['default'][0])
        if user_id == -1:
            await message.reply("User not found")
            return
        await message.reply(f"Fetching first places...")

        first_places = cache.lookup_first_places(user_id, mode, relax)
        if 'max_accuracy' in parsed:
            max_acc = float(parsed['max_accuracy'])
            new_firsts = []
            for score in first_places:
                if score.accuracy <= max_acc:
                    new_firsts.append(score)
            first_places = new_firsts
        if 'min_accuracy' in parsed:
            min_acc = float(parsed['min_accuracy'])
            new_firsts = []
            for score in first_places:
                if score.accuracy >= min_acc:
                    new_firsts.append(score)
            first_places = new_firsts
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
        if 'min_pp' in parsed:
            min_pp = float(parsed['min_pp'])
            new_firsts = []
            for score in first_places:
                if score.pp >= min_pp:
                    new_firsts.append(score)
            first_places = new_firsts
        if 'max_pp' in parsed:
            max_pp = float(parsed['max_pp'])
            new_firsts = []
            for score in first_places:
                if score.pp <= max_pp:
                    new_firsts.append(score)
            first_places = new_firsts
        if 'max_combo' in parsed:
            max_combo = int(parsed['max_combo'])
            new_firsts = []
            for score in first_places:
                if score.max_combo <= max_combo:
                    new_firsts.append(score)
            first_places = new_firsts
        if 'min_combo' in parsed:
            min_combo = int(parsed['min_combo'])
            new_firsts = []
            for score in first_places:
                if score.max_combo >= min_combo:
                    new_firsts.append(score)
            first_places = new_firsts
        await FirstPlacesView(f"First places for {user_id}", first_places).reply(message)

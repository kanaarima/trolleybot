import discord
from command import Command
from mods import Mods
from skills import get_all_skillsets
from api.bancho import get_beatmap
import pp

class TestSkill(Command):
    
    def __init__(self) -> None:
        super().__init__("whatskillset", "test what skillset is a specific map")
    
    async def run(self, message: discord.Message, args: list[str], parsed: dict[str, str]):
        if len(parsed['default']) < 2:
            await message.channel.send("Please specify a map! t!whatskillset map_id mods")
            return
        id = parsed['default'][0]
        mods = Mods.from_string(parsed["default"][1]).value
        beatmap = get_beatmap(id)
        if not beatmap:
            await message.channel.send("Could not find beatmap")
            return
        attributes = pp.calc_attributes(id, 0, mods)
        embed = discord.Embed(title="Skillsets for map X")
        for skillset in get_all_skillsets():
            embed.add_field(name=skillset.name, value=f"Match: {skillset.matches(beatmap, attributes)}, Points: {skillset.calculate_skillset_points(beatmap, attributes)}", inline=False)
        await message.reply(embed=embed)
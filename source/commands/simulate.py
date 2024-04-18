from akatsuki_pp_py import Beatmap, Calculator
from command import Command
from mods import Mods

import discord
import pp

beatmap_parameters = ['od', 'ar', 'cs']
calculator_parameters = ['mods', 'acc', 'n300', 'n100', 'n50', 'n_misses', 'n_geki', 'n_katu', 'combo', 'passed_objects']


class Simulate(Command):
    def __init__(self) -> None:
        super().__init__('simulate', 'Simulate pp', ['pp', 'simulate', 'm'])
        self.help = f"""
        Arguments: <beatmap_id> <-mode> (-param value)
        Modes: std/std_rx/std_ap/taiko/taiko_rx/ctb/ctb_rx/mania
        Beatmap parameters: {', '.join(beatmap_parameters)}
        Calculator parameters: {', '.join(calculator_parameters)}
        """

    async def run(self, message: discord.Message, args: list[str],  parsed: dict[str, str]):
        if len(parsed['default']) == 0 or not parsed['default'][0].isnumeric():
            await message.reply("Please specify a beatmap ID!")
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        beatmap_id = int(parsed['default'][0])
        content = pp._get_beatmap(beatmap_id)
        if not content:
            await message.reply("Can't find beatmap!")
            return
        beatmap_args = {'bytes': content}
        calculator_args = {'mode': mode}
        for param in beatmap_parameters:
            if param in parsed:
                beatmap_args[param] = float(parsed[param])
        for param in calculator_parameters:
            if param in parsed:
                if param == 'mods':
                    calculator_args[param] = Mods.from_string(parsed[param]).value
                else:
                    if parsed[param].isnumeric():
                        calculator_args[param] = int(parsed[param])
                    else:
                        calculator_args[param] = float(parsed[param])
        beatmap = Beatmap(**beatmap_args)
        calculator = Calculator(**calculator_args)
        performance = calculator.performance(beatmap)
        embed = discord.Embed(title="Simulated pp", color=discord.Color.dark_magenta())
        embed.description = ""
        if mode == 0:
            embed.description = f"**Max pp**: {performance.pp:.0f}"
            if performance.pp_aim > 0:
                embed.description += f" (**Aim pp**: {performance.pp_aim:.0f}, **Speed pp**: {performance.pp_speed:.0f}, **Acc/FL**: {performance.pp - (performance.pp_aim + performance.pp_speed):.0f})"
            else:
                embed.description += f" (**Speed pp**: {performance.pp_speed:.0f}, **Acc/FL**: {performance.pp - performance.pp_speed:.0f})"
        else:
            embed.description = f"**Max pp**: {performance.pp:.0f}"
        if mode == 0:
            embed.description += f"\n**SR**: {performance.difficulty.stars:.1f} | **Speed SR**: {performance.difficulty.speed:.1f}"
            if performance.pp_aim > 0:
                embed.description += f" | **Aim SR**: {performance.difficulty.aim:.1f}"
        else:
            embed.description += f"\n**SR**: {performance.difficulty.stars:.1f}"
        embed.description += f"\n[Direct](https://kanaarima.github.io/osu/osudl.html?beatmap={beatmap_id}) [Bancho](https://osu.ppy.sh/b/{beatmap_id}) [Akatsuki](https://akatsuki.gg/b/{beatmap_id})"
        await message.reply(embed=embed)

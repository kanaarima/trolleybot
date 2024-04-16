import discord

class Command:
    
    def __init__(self, command_name: str, description: str, triggers: list[str] = list()) -> None:
        self.command_name = command_name
        self.description = description
        self.triggers = triggers if triggers else [command_name]
        self.help = "No help provided."
    
    def is_me(self, trigger):
        if trigger == self.command_name:
            return True
        for t in self.triggers:
            if t == trigger:
                return True
        return False
    
    def parse_args(self, args: list[str]) -> dict:
        modes = {'std': (0,0), 'std_rx': (0,1), 'std_ap': (0,2), 'taiko': (1,0), 'taiko_rx': (1,1), 'ctb': (2,0), 'ctb_rx': (2,1), 'mania': (3,0)}
        parsed = {'default': list()}
        pre = ""
        for arg in args:
            if arg[0] == '-':
                if arg[1:] in modes:
                    parsed['mode'] = modes[arg[1:]]
                    continue
                if pre:
                    parsed[pre] = ''
                    pre = None
                else:
                    pre = arg[1:]
            else:
                if pre:
                    parsed[pre] = arg
                    pre = None
                else:
                    parsed['default'].append(arg)
        if pre:
            parsed[pre] = ''
        return parsed
    
    def get_mode_full_name(self, mode, relax):
        base_mode = ['standard', 'taiko', 'catch the beat', 'mania']
        base_relax = ['', ' relax', ' autopilot']
        return f"{base_mode[mode]}{base_relax[relax]}"
    
    async def run(self, message: discord.Message, args: list[str], parsed: dict[str, str]):
        raise NotImplementedError
import discord

class Command:
    
    def __init__(self, command_name: str, description: str, triggers: list[str] = list()) -> None:
        self.command_name = command_name
        self.description = description
        self.triggers = triggers if triggers else [command_name]
    
    def is_me(self, trigger):
        if trigger == self.command_name:
            return True
        for t in self.triggers:
            if t == trigger:
                return True
        return False
    
    async def run(self, message: discord.Message, args: list[str]):
        raise NotImplementedError
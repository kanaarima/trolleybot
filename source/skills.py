from api.bancho import Beatmap
from pp import Attributes

class Skill:
    
    def __init__(self, name, description):
        self.name = name
        self.description = description
        
    def matches(self, beatmap: Beatmap, attributes: Attributes) -> float:
        return 0.0

    def calculate_skillset_points(self, beatmap: Beatmap, attributes: Attributes) -> float:
        0

class StreamSkill(Skill):
    def __init__(self):
        super().__init__("Stream", "Stream skillset")
    
    def matches(self, beatmap: Beatmap, attributes: Attributes) -> float:
        speed_acc = attributes.speed_pp + (attributes.acc_pp)
        if speed_acc < attributes.aim_pp:
            return 0.0
        else:
            return attributes.aim_pp / speed_acc

    def calculate_skillset_points(self, beatmap: Beatmap, attributes: Attributes) -> float:
        multiplier = self.matches(beatmap, attributes)
        return (attributes.speed_pp + attributes.aim_pp) * multiplier

class AimSkill(Skill):
    
    def __init__(self):
        super().__init__("Aim", "Jump map")
    
    def matches(self, beatmap: Beatmap, attributes: Attributes) -> float:
        aim_acc = attributes.aim_pp + attributes.acc_pp
        if aim_acc < attributes.speed_pp:
            return 0.0
        else:
            return aim_acc 
    
    def calculate_skillset_points(self, beatmap: Beatmap, attributes: Attributes) -> float:
        multiplier = self.matches(beatmap, attributes)
        return attributes.aim_pp * multiplier


def get_all_skillsets() -> list[Skill]:
    return [StreamSkill(), AimSkill()]
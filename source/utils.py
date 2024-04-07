
import math
from mods import Mods


class Model:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class MapStats:
    
    OD0_MS = 80
    OD10_MS = 20
    AR0_MS = 1800.0
    AR5_MS = 1200.0
    AR10_MS = 450.0
    OD_MS_STEP = (OD0_MS - OD10_MS) / 10.0
    AR_MS_STEP1 = (AR0_MS - AR5_MS) / 5.0
    AR_MS_STEP2 = (AR5_MS - AR10_MS) / 5.0

    def __init__(self, mods: int, ar: float, od: float, hp: float, cs: float, bpm: float) -> None:
        self.ar = ar
        self.od = od
        self.hp = hp
        self.cs = cs
        self.bpm = bpm
        self.mods = Mods(mods).members
        
        speed = 1
        od_ar_hp_multiplier = 1.0
        
        if Mods.DoubleTime in self.mods or Mods.Nightcore in self.mods:
            speed = 1.5
        
        if Mods.HalfTime in self.mods:
            speed = 0.75

        self.bpm *= speed
        
        if Mods.HardRock in self.mods:
            od_ar_hp_multiplier = 1.4
            self.cs = min(self.cs*1.3, 10)

        if Mods.Easy in self.mods:
            od_ar_hp_multiplier = 0.5
            self.cs *= 0.5
        
        self.ar *= od_ar_hp_multiplier
        self.hp = min(10, self.hp * od_ar_hp_multiplier)
        
        if self.ar < 5:
            arms = self.AR0_MS - self.AR_MS_STEP1 * self.ar
        else:
            arms = self.AR5_MS - self.AR_MS_STEP2 * (self.ar - 5)
        
        arms = min(self.AR0_MS, max(self.AR10_MS, arms)) / speed

        if arms > self.AR5_MS:
            self.ar = (self.AR0_MS - arms) / self.AR_MS_STEP1
        else:
            self.ar = 5.0 + (self.AR5_MS - arms) / self.AR_MS_STEP2
        
        odms = self.OD0_MS - math.ceil(self.OD_MS_STEP * self.od)
        odms /= speed
        self.od = (self.OD0_MS - odms) / self.OD_MS_STEP
import json
from akatsuki_pp_py import Beatmap, Calculator
from utils import Model

import requests
import os

DEFAULT_HEADERS = {"user-agent": "akatsukialt!/KompirBot fetch service"}

def _ppy_download(beatmap_id) -> bytes:
    response = requests.get(
        f"https://old.ppy.sh/osu/{beatmap_id}",
        headers=DEFAULT_HEADERS,
    )
    if not response.ok or not response.content:
        return
    #logger.info(f"GET {response.url} {response.status_code}")
    with open (f"../cache/beatmaps/{beatmap_id}.osz", 'wb') as f:
        f.write(response.content)
    return response.content

def _get_beatmap(beatmap_id: int) -> bytes:
    if os.path.exists(f"../cache/beatmaps/{beatmap_id}.osz"):
        with open(f"../cache/beatmaps/{beatmap_id}.osz", 'rb') as f:
            return f.read()
    else:
        return _ppy_download(beatmap_id)

class Attributes(Model):
    max_pp: float
    aim_pp: float
    speed_pp: float
    acc_pp: float
    
    ar_hit_window: float
    ar: float
    cs: float
    od: float
    
    n_circles: int
    n_sliders: int
    n_spinners: int
    
    def from_json(dict):
        return Attributes(**dict)
    
    def to_json(self):
        return self.__dict__

def calc_attributes(beatmap_id: int, mode: int, mods: int, accuracy: float = 100, count_n300 = 0, count_n100 = 0, count_n50 = 0, count_misses = 0) -> Attributes:
    filename = f"../cache/pp/{beatmap_id}_{mode}_{mods}_{accuracy}_{count_n300}_{count_n100}_{count_n50}_{count_misses}.json"
    if os.path.exists(filename):
        with open(filename) as f:
            return Attributes.from_json(json.load(f))
    content = _get_beatmap(beatmap_id)
    if not content:
        return
    beatmap = Beatmap(bytes=content)
    calculator = Calculator(mode=mode, mods=mods)
    calculator.set_acc(accuracy)
    if count_n300 or count_n100 or count_n50 or count_misses:
        calculator.set_n300(count_n300)
        calculator.set_n100(count_n100)
        calculator.set_n50(count_n50)
        calculator.set_n_misses(count_misses)
    performance = calculator.performance(beatmap)
    map_attributes = calculator.map_attributes(beatmap)
    attrs =  Attributes(
        max_pp=performance.pp,
        aim_pp=performance.pp_aim,
        speed_pp=performance.pp_speed,
        acc_pp=performance.pp - (performance.pp_aim + performance.pp_speed),
        ar_hit_window=map_attributes.ar_hit_window,
        ar=map_attributes.ar,
        cs=map_attributes.cs,
        od=map_attributes.od,
        n_circles=map_attributes.n_circles,
        n_sliders=map_attributes.n_sliders,
        n_spinners=map_attributes.n_spinners
    )
    with open(filename, 'w') as f:
        json.dump(attrs.to_json(), f)
    return attrs
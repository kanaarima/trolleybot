import json
import os
from ossapi import Ossapi
import config
from utils import Model

client = Ossapi(client_id=config.OSU_V2_CLIENT, client_secret=config.OSU_V2_SECRET)

class Beatmap(Model):
    beatmap_id: int
    beatmapset_id: int
    beatmap_md5: str
    artist: str
    title: str
    version: str
    creator: str
    max_combo: int
    hit_length: int
    total_length: int
    bpm: float
    ar: float
    od: float
    cs: float
    hp: float

    def from_cache(dict):
        beatmap = Beatmap(**dict)
        return beatmap
    
    def to_cache(self):
        cache = dict()
        for k, v in self.__dict__.items():
            cache[k] = v
        return cache

    def from_akat_beatmap(akat_beatmap):
        split = akat_beatmap.song_name.split(" - ", 1)
        artist = split[0]
        title = split[1].split(" [")
        diff_name = title[1][:-1]
        title = title[0]
        return Beatmap(
            beatmap_id=akat_beatmap.beatmap_id,
            beatmapset_id=akat_beatmap.beatmapset_id,
            beatmap_md5=akat_beatmap.beatmap_md5,
            artist=artist,
            title=title,
            version=diff_name,
            creator="Unknown",
            max_combo=akat_beatmap.max_combo,
            hit_length=akat_beatmap.hit_length,
            total_length=akat_beatmap.hit_length,
            bpm=-1,
            ar=akat_beatmap.ar,
            od=akat_beatmap.od,
            hp=-1,
            cs=-1,
        )
        
def get_beatmap(beatmap_id) -> Beatmap:
    try:
        api_beatmap = client.beatmap(beatmap_id)
        api_beatmapset = api_beatmap.beatmapset()
    except:
        return None
    return Beatmap(
        beatmap_id=api_beatmap.id,
        beatmapset_id=api_beatmap.beatmapset_id,
        beatmap_md5=api_beatmap.checksum,
        artist=api_beatmapset.artist,
        title=api_beatmapset.title,
        version=api_beatmap.version,
        creator=api_beatmapset.creator,
        max_combo=api_beatmap.max_combo,
        hit_length=api_beatmap.hit_length,
        total_length=api_beatmap.total_length,
        bpm=api_beatmapset.bpm,
        ar=api_beatmap.ar,
        od=api_beatmap.accuracy,
        cs=api_beatmap.cs,
        hp=api_beatmap.drain
    )
        
def get_beatmap_cached(beatmap_id: int) -> Beatmap:
    if os.path.exists(f"../cache/beatmaps/{beatmap_id}.json"):
        with open(f"../cache/beatmaps/{beatmap_id}.json") as f:
            return Beatmap.from_cache(json.load(f))
    beatmap = get_beatmap(beatmap_id)
    if beatmap is None:
        return None
    with open(f"../cache/beatmaps/{beatmap_id}.json", 'w') as f:
        json.dump(beatmap.to_cache(), f)
    return beatmap

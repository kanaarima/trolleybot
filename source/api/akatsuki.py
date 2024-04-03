from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple
from utils import Model

import requests
import time

DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

class AkatsukiBeatmap(Model):
    beatmap_id: int
    beatmapset_id: int
    beatmap_md5: str
    song_name: str
    ar: float
    od: float
    difficulty: float # Useless
    max_combo: int
    hit_length: int
    ranked: int
    ranked_status_frozen: int
    latest_update: datetime

    def from_dict(dict):
        beatmap = AkatsukiBeatmap(**dict)
        beatmap.latest_update = datetime.strptime(beatmap.latest_update, DATE_FORMAT)
        return beatmap

class Score(Model):
    id: int
    beatmap_md5: str
    score: int
    max_combo: int
    full_combo: bool
    mods: int
    count_300: int
    count_100: int
    count_50: int
    count_geki: int
    count_katu: int
    count_miss: int
    time: datetime
    play_mode: int
    accuracy: float
    pp: float
    rank: str
    completed: int
    pinned: bool
    beatmap: AkatsukiBeatmap

    def from_dict(dict):
        score = Score(**dict)
        score.time = datetime.strptime(score.time, DATE_FORMAT)
        if 'beatmap' in dict:
            score.beatmap = AkatsukiBeatmap.from_dict(dict['beatmap'])
        return score


class Akatsuki:
    
    def __init__(self, req_min=60):
        self.req_min = req_min
        self.last_request = time.time()
    
    def request(self, url):
        delay = 60/self.req_min
        if time.time() - self.last_request < delay:
            time.sleep(delay - (time.time() - self.last_request))
        return requests.get(url)
    
    def get_user_first_places(self, user_id: int, mode: int, relax: int) -> Tuple[List[Score], int]:
        first_places = list()
        page = 1
        while True:
            req = self.request(f"https://akatsuki.gg/api/v1/users/scores/first?mode={mode}&p={page}&l=100&rx={relax}&id={user_id}")
            if req.status_code != 200 or not req.json()['scores']:
                break
            first_places += [Score.from_dict(score) for score in req.json()['scores']]
            page += 1
        return first_places, req.json()['total']

    
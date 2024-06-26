from dataclasses import dataclass
from bs4 import BeautifulSoup
from api.bancho import Beatmap
from datetime import datetime
from utils import Model
from typing import *

import api.bancho as bancho
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

    def from_cache(dict):
        return AkatsukiBeatmap.from_dict(dict)

    def to_cache(self):
        cache = dict()
        for k, v in self.__dict__.items():
            if k == 'latest_update':
                cache[k] = v.strftime(DATE_FORMAT)
            else:
                cache[k] = v
        return cache

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
    actual_beatmap: Beatmap = None

    def from_dict(dict):
        score = Score(**dict)
        score.time = datetime.strptime(score.time, DATE_FORMAT)
        if 'beatmap' in dict:
            score.beatmap = AkatsukiBeatmap.from_dict(dict['beatmap'])
            score.actual_beatmap = bancho.get_beatmap_cached(score.beatmap.beatmap_id)
        return score

    def from_cache(dict):
        return Score.from_dict(dict)

    def to_cache(self):
        cache = dict()
        for k, v in self.__dict__.items():
            if k == 'time':
                cache[k] = v.strftime(DATE_FORMAT)
            elif k == 'beatmap':
                cache[k] = v.to_cache()
            elif k == 'actual_beatmap':
                continue
            else:
                cache[k] = v
        return cache

class ClanInfo(Model):
    id: int
    name: str
    tag: str
    description: str
    icon: str
    owner: int
    status: int

class Stats(Model):
    ranked_score: int
    total_score: int
    playcount: int
    playtime: int
    replays_watched: int
    total_hits: int
    level: float
    accuracy: float
    pp: int
    global_leaderboard_rank: int
    country_leaderboard_rank: int
    max_combo: int

class UserInfo(Model):
    id: int
    username: str
    username_aka: str # Unused
    registered_on: datetime
    priviledges: int
    latest_activity: datetime
    country: str
    stats: List[Dict[str, Stats]]
    play_style: int
    favourite_mode: int
    clan: ClanInfo
    followers: int
    
    def from_dict(dict):
        user = UserInfo(**dict)
        user.registered_on = datetime.strptime(user.registered_on, DATE_FORMAT)
        user.latest_activity = datetime.strptime(user.latest_activity, DATE_FORMAT)
        if 'stats' in dict:
            user.stats = [{k: Stats(**v) for k, v in stats.items()} for stats in dict['stats']]
        if 'clan' in dict:
            user.clan = ClanInfo(**dict['clan'])
        return user
    

class Akatsuki:
    
    def __init__(self, req_min=60):
        self.req_min = req_min
        self.last_request = time.time()
    
    def request(self, url):
        delay = 60/self.req_min
        if time.time() - self.last_request < delay:
            time.sleep(delay - (time.time() - self.last_request))
        return requests.get(url)
    
    def get_user_first_places(self, user_id: int, mode: int, relax: int, count_only: bool) -> Tuple[List[Score], int]:
        first_places = list()
        page = 1
        while True:
            req = self.request(f"https://akatsuki.gg/api/v1/users/scores/first?mode={mode}&p={page}&l=100&rx={relax}&id={user_id}")
            if req.status_code != 200 or not req.json()['scores']:
                break
            if count_only:
                return [], req.json()['total']
            first_places += [Score.from_dict(score) for score in req.json()['scores']]
            page += 1
        return first_places, req.json()['total']

    def get_user_best(self, user_id: int, mode: int, relax: int, page: int = 1) -> List[Score]:
        req = self.request(f"https://akatsuki.gg/api/v1/users/scores/best?mode={mode}&p={page}&l=100&rx={relax}&id={user_id}")
        return [Score.from_dict(score) for score in req.json()['scores']]

    def get_user_stats(self, user_id: int) -> UserInfo:
        req = self.request(f"https://akatsuki.gg/api/v1/users/full?id={user_id}")
        if req.status_code != 200:
            return None
        return UserInfo.from_dict(req.json())

    def lookup_user(self, username: str) -> int:
        req = self.request(f"https://akatsuki.gg/api/v1/users/lookup?name={username}")
        if not req.status_code == 200 or not req.json()['users']:
            return -1
        for user in req.json()['users']:
            if user['username'].lower() == username.lower():
                return user['id']
        return -1
    
    def get_clan_members(self, clan_id: int):
        req = self.request(f"https://akatsuki.gg/c/{clan_id}?mode=0&rx=1")
        bs4 = BeautifulSoup(req.text, 'html.parser')
        players = bs4.find_all('a', class_="player")
        members = list()
        for player in players:
            try:
                members.append(int(player['href'].split('/')[-1]))     
            except:
                print("Cant process one restricted user!")
                continue
        return members   
    
instance = Akatsuki()
    
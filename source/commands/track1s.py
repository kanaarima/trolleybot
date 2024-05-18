import io
import time

import requests
from command import Command

from api.akatsuki import Score, instance
import datetime
import discord

from mods import Mods

class Track1s(Command):
    def __init__(self):
        super().__init__("start1strack", "Track 1s", ["start1strack"])

    async def run(self, message: discord.Message, args: list[str], parsed: dict[str, str]):
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        userid = 0
        if parsed['default'][0].isnumeric():
            userid = int(parsed['default'][0])
        else:
            userid = instance.lookup_user(parsed['default'][0])
        if userid == -1:
            await message.reply("User not found")
            return
        with open(f"../cache/{message.author.id}_{userid}_{mode}_{relax}.json", 'w') as f:
            f.write(datetime.datetime.now().isoformat())
        await message.reply("Tracking started!")

class Stop1sTrack(Command):
    
    def __init__(self):
        super().__init__("stop1strack", "Track 1s", ["stop1strack"])
        self.last_request = time.time()
        self.req_min = 60

    def request(self, url):
        delay = 60/self.req_min
        if time.time() - self.last_request < delay:
            time.sleep(delay - (time.time() - self.last_request))
        return requests.get(url)

    async def run(self, message: discord.Message, args: list[str], parsed: dict[str, str]):
        if 'mode' in parsed:
            mode, relax = parsed['mode']
        else:
            mode, relax = 0,0
        userid = 0
        if parsed['default'][0].isnumeric():
            userid = int(parsed['default'][0])
        else:
            userid = instance.lookup_user(parsed['default'][0])
        if userid == -1:
            await message.reply("User not found")
            return
        try:
            with open(f"../cache/{message.author.id}_{userid}_{mode}_{relax}.json") as f:
                date = datetime.datetime.fromisoformat(f.readline())
            first_places = list()
            page = 1
            while True:
                req = self.request(f"https://akatsuki.gg/api/v1/users/scores/first?mode={mode}&p={page}&l=100&rx={relax}&id={userid}")
                if req.status_code != 200 or not req.json()['scores']:
                    break
                furk = False
                for first_place in [Score.from_dict(score) for score in req.json()['scores']]:
                    if first_place.time > date:
                        first_places.append(first_place)
                    else:
                        furk = True
                        break
                if furk:
                    break
                page += 1
            csv = "link,title,mods,accuracy,previous_holder\n"
            for first_place in first_places:
                previous_holder = "No one"
                lb = self.request(f"https://akatsuki.gg/api/v1/scores?sort=pp,desc&m={mode}&relax={relax}&b={first_place.beatmap.beatmap_id}&p=1&l=3").json()
                if len(lb['scores']) > 1:
                    previous_holder = lb['scores'][1]['user']['username']
                csv += f"https://akatsuki.gg/b/{first_place.beatmap.beatmap_id}?mode={mode}&rx={relax},{first_place.beatmap.song_name},{Mods(first_place.mods).short},{first_place.accuracy:.2f}%,{previous_holder}\n"
            await message.reply(f"First place obtained: {len(first_places)}", file=discord.File(fp=io.BytesIO(csv.encode("utf-8")), filename="first_places.csv"))
        except FileNotFoundError:
            await message.reply("Start tracking first!")
            return
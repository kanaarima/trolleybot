from api.akatsuki import Score, instance

import json
import time
import os

os.makedirs("../cache", exist_ok=True)
os.makedirs("../cache/beatmaps", exist_ok=True)
os.makedirs("../cache/first_places", exist_ok=True)

def calc_cache_seconds(total_count):
    if total_count < 3000:
        return max((300/instance.req_min) * (total_count / 100), 300)
    else:
        return 86400

def lookup_first_places(user_id, mode, relax) -> list[Score]:    
    if os.path.exists(f"../cache/first_places/{user_id}_{mode}_{relax}.json"):
        with open(f"../cache/first_places/{user_id}_{mode}_{relax}.json") as f:
            cache = json.load(f)
            time_passed = time.time() - cache['time']
            if time_passed < calc_cache_seconds(len(cache['cache'])):
                first_places = list()
                for first_place in cache['cache']:
                    first_places.append(Score.from_cache(first_place))
                return first_places
    cache = list()
    first_places = instance.get_user_first_places(user_id, mode, relax, False)[0]
    for first_place in first_places:
        cache.append(first_place.to_cache())
    with open(f"../cache/first_places/{user_id}_{mode}_{relax}.json", 'w') as f:
        json.dump({'time': time.time(), 'cache': cache}, f)
    return first_places
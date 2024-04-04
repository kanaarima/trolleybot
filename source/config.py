import json

with open("../secrets.json") as f:
    config = json.load(f)
    DISCORD_BOT_TOKEN = config['discord_bot_token']
    OSU_V2_CLIENT = config['osu_v2_client']
    OSU_V2_SECRET = config['osu_v2_secret']
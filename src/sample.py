import datetime
import logging
import random

import discord
from discord.ext import tasks
from dotenv import dotenv_values

from meme import meme_dict

logger = logging.getLogger("sample")
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

x_api_key = config["x_api_key"]
x_api_key_secret = config["x_api_key_secret"]
x_access_token = config["x_access_token"]
x_access_token_secret = config["x_access_token_secret"]
x_bearer_token = config["x_bearer_token"]

STEAM_WEB_API_KEY = config["STEAM_WEB_API_KEY"]
STEAM_MY_UID = config["STEAM_MY_UID"]


@tasks.loop(minutes=60)
async def loop():
    now = datetime.datetime.now().strftime("%H:%M")
    # print(f"loop {now=}")

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await loop.start()

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # 1. Setup dict have startswith strings and image string.
    # 2. If message.content.startswith(dict.keys()), send dict.values() image.
    # 3. multi values, random.choice(values)
    for key, value in meme_dict.items():
        if message.content.startswith(key):
            if isinstance(value, list):
                await message.channel.send("", file=discord.File(f"{random.choice(value)}"))
            else:
                await message.channel.send("", file=discord.File(f"{value}"))
    if message.content.startswith("$meme_list"):
        await message.channel.send(f"{meme_dict.keys()}")
    if message.content.startswith("$meme_help"):
        await message.channel.send(f"$meme_list: ミーム一覧の表示")

    if message.content.startswith("これドクターストーン最新話です。"):
        await message.add_reaction("👀")
        await message.channel.send("https://www.netflix.com/browse?jbv=81046193")

# logger.info(config['token'])
client.run(config["token"])

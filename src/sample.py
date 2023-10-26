import sys
import datetime
import logging
import random

import discord
from discord.ext import tasks
from dotenv import dotenv_values

from counter import get_counter_group_id, try_increment_counter
from data.counter_kawaki import CounterKawaki
from db import session_scope
from data.meme import meme_dict

logger = logging.getLogger("sample")
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

COUNTER_REACTION = {
    True: "✅",
    False: "❌",
}


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
                await message.channel.send(
                    "", file=discord.File(f"{random.choice(value)}")
                )
            else:
                await message.channel.send("", file=discord.File(f"{value}"))
    if message.content.startswith("$meme_list"):
        await message.channel.send(f"{meme_dict.keys()}")
    if message.content.startswith("$meme_help"):
        await message.channel.send(f"$meme_list: ミーム一覧の表示")

    if message.content.startswith("これドクターストーン最新話です。"):
        await message.add_reaction("👀")
        await message.channel.send("https://www.netflix.com/browse?jbv=81046193")

    for i, v in enumerate(CounterKawaki.data):
        if message.content.startswith(v):
            with session_scope() as _:
                counter_group_id = get_counter_group_id(CounterKawaki.name)
                result = try_increment_counter(message.author.id, counter_group_id, i + 1)
                await message.add_reaction(COUNTER_REACTION[result["status"]])
                if result["status"] and i == CounterKawaki.max_count - 1:
                    await message.channel.send(CounterKawaki.complete_msg)

# logger.info(config['token'])

# config["token"] is str or none. but client.run() need str.
# how to error handling?

if config["token"] is None:
    logger.error("token is None.")
    sys.exit(1)
else:
    client.run(config["token"])

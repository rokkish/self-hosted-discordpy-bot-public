import sys
import datetime
import logging
import random

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import dotenv_values

from counter import get_counter_group_id, try_increment_counter
from data.counter_kawaki import CounterKawaki
from db import session_scope
from data.meme import meme_dict, meme_dict_txt, meme_dict_txt_endswith

logger = logging.getLogger("sample")
logger.setLevel(logging.DEBUG)

config = dotenv_values(".env")

class MorganaClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.MY_GUILD = discord.Object(id=config["DISCORD_GUILD_ID"])

    async def setup_hook(self) -> None:
        self.tree.copy_global_to(guild=self.MY_GUILD)
        await self.tree.sync(guild=self.MY_GUILD)

intents = discord.Intents.default()
intents.message_content = True

client = MorganaClient(intents=intents)

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

    # reply meme(txt)
    for key, value in meme_dict_txt.items():
        if message.content.endswith(key):
            if isinstance(value, list):
                await message.channel.send(
                    f"{random.choice(value)}"
                )
            elif isinstance(value, str):
                await message.channel.send(f"{value}")
            else:
                await message.channel.send(f"{value()}")

    # reply meme(txt) ends with
    for key, value in meme_dict_txt_endswith.items():
        if message.content.endswith(key):
            if isinstance(value, list):
                await message.channel.send(
                    f"{random.choice(value)}"
                )
            else:
                await message.channel.send(f"{value}")

    for i, v in enumerate(CounterKawaki.data):
        if message.content.startswith(v):
            with session_scope() as _:
                counter_group_id = get_counter_group_id(CounterKawaki.name)
                result = try_increment_counter(message.author.id, counter_group_id, i + 1)
                await message.add_reaction(COUNTER_REACTION[result["status"]])
                if result["status"] and i == CounterKawaki.max_count - 1:
                    await message.channel.send(CounterKawaki.complete_msg)

    try:
        if quiz:
            if quiz.is_correct(message.content):
                quiz.update_answered()
                logger.debug("correct!")
                return
            if quiz.is_close(message.content):
                masked_title = quiz.get_masked_title(message.content)
                await message.channel.send(f"> {message.content}\n惜しい！{masked_title}")
    except NameError:
        pass

@client.tree.command(
    name="quiz",
    description="連想されるキーワードを当ててくれ!",
)
@app_commands.describe(theme="好きなテーマを単語で入力してくれ！")
async def quiz_morgana(interaction: discord.Interaction, theme: str) -> None:
    """クイズを出題する関数"""
    from quiz import Quiz
    import time
    global quiz

    if interaction.channel_id != int(config["DISCORD_CHANNEL_ID_QUIZ"]):
        await interaction.response.send_message(f"このチャンネルでは無効だ！")
        return

    channel = client.get_channel(interaction.channel_id)

    await interaction.response.send_message(f"テーマは{theme}だな！")

    quiz = Quiz()
    try:
        quiz.setup_quiz(theme)
    except Exception("No title candidates") as e:
        await channel.send(f"エラーが発生したぞ！\n{e}")
        return
    time.sleep(1)

    await channel.send(f"じゃあ始めるぜ\n----------------------------------\n")

    for i in range(quiz.NUM_MAX_HINT):
        if i == quiz.NUM_MAX_HINT // 4:
            # len(quiz.title) x 〇 の文字列を表示する
            await channel.send(f"ヒント：{quiz.get_masked_title('')}")
        if i == quiz.NUM_MAX_HINT * 1 // 2:
            part_title = quiz.get_part_of_title(0.2)
            await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")
        if i == quiz.NUM_MAX_HINT * 3 // 4:
            part_title = quiz.get_part_of_title(0.5)
            await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")
        if quiz.already_answered:
            break
        time.sleep(1)
        msg = f"{i+1}/{quiz.NUM_MAX_HINT}: "
        if quiz.exist_hint("LOW"):
            msg += quiz.get_hint("LOW")
            await channel.send(f"{msg}")
            continue
        if quiz.exist_hint("HIGH"):
            msg += quiz.get_hint("HIGH")
            await channel.send(f"{msg}")
            continue

    for i in range(50):
        if quiz.already_answered:
            break
        time.sleep(0.1)
    if not quiz.already_answered:
        await channel.send(f"----------------------------------\n")

    if not quiz.already_answered:
        part_title = quiz.get_part_of_title(0.7)
        await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")

    for i in range(50):
        if quiz.already_answered:
            break
        time.sleep(0.1)
    if not quiz.already_answered:
        await channel.send(f"### 大ヒント！(X: 答え, Y: 読み仮名やアルファベット, Z: 答えに含まれる文字）\n{quiz.summary}")

    for i in range(100):
        if quiz.already_answered:
            break
        time.sleep(0.1)

    if quiz.already_answered:
        await channel.send("おめでとう！正解だ！")
    else:
        await channel.send(f"----------------------------------\n残念 時間切れだ...")
    await channel.send(f"正解は**{quiz.get_answer()}**だ！\n{quiz.get_answer_url()}")

# logger.info(config['token'])

# config["token"] is str or none. but client.run() need str.
# how to error handling?

if config["token"] is None:
    logger.error("token is None.")
    sys.exit(1)
else:
    client.run(config["token"])

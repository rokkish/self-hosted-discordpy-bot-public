import sys
import enum
import datetime
import logging
import logging.config
import random
import yaml

import discord
from discord import app_commands
from discord.ext import tasks
from dotenv import dotenv_values

from counter import get_counter_group_id, try_increment_counter
from data.counter_kawaki import CounterKawaki
from db import session_scope
from data.meme import meme_dict, meme_dict_txt, meme_dict_txt_endswith

logger = logging.getLogger("morgana")
# load logging.yml
with open("src/logging.yml", "r") as f:
    logging.config.dictConfig(yaml.safe_load(f))

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
                await message.channel.send("おめでとう！正解だ！")
                return
            if quiz.is_close(message.content):
                masked_title = quiz.get_masked_title(message.content)
                await message.channel.send(f"> {message.content}\n惜しい！{masked_title}")
    except NameError:
        pass

@client.tree.command(
    name="qquiz",
    description="進行中のクイズを強制終了させる！(quit quiz)",
)
async def quit_quiz(interaction: discord.Interaction) -> None:
    global quiz
    try:
        quiz.already_answered = True
        quiz.force_answer = True
        await interaction.response.send_message(f"クイズを強制終了したぞ！")
    except NameError:
        await interaction.response.send_message(f"強制終了するクイズはないぞ！")

class ProgressBar(object):
    def __init__(self, total: int) -> None:
        self.total = total
        self.cursor = 0
    def print(self, msg: str) -> str:
        x = "x" * self.cursor
        dot = "-" * (self.total - self.cursor)
        self.cursor += 1
        return f"[{x}{dot}] {msg}"

import time
def wait(seconds: int) -> None:
    global quiz
    sleep_time = 0.1
    loop_num = int(seconds / sleep_time)
    for _ in range(loop_num):
        if quiz.already_answered:
            break
        time.sleep(sleep_time)
    return

from quiz_genre import QuizGenresChoices
@client.tree.command(
    name="quiz_genre",
    description="連想されるキーワードを当ててくれ!",
)
@app_commands.describe(
    genre="ジャンルを選んでくれ！",
)
async def quiz_morgana_genre(interaction: discord.Interaction, genre: QuizGenresChoices) -> None:
    """クイズを出題する関数"""
    from quiz import Quiz
    global quiz

    if not interaction.channel_id in [int(config["DISCORD_CHANNEL_ID_QUIZ"]), int(config["DISCORD_CHANNEL_ID_QUIZ_DEBUG"])]:
        await interaction.response.send_message(f"このチャンネルでは無効だ！")
        return

    # use singleton pattern, global quiz object is singleton
    if "quiz" in globals() and not quiz.force_answer:
        await interaction.response.send_message(f"クイズは既に進行中だ！")
        return

    channel = client.get_channel(interaction.channel_id)

    p_bar = ProgressBar(total=4)
    msg = f"ジャンルは{genre.name}だな！"
    await interaction.response.send_message(f"{p_bar.print(msg)}")
    send_msg = await interaction.original_response()

    try:
        quiz = Quiz(NUM_MAX_HINT=20)
        # quiz.setup_quiz(theme)
        theme = quiz.pick_theme_from_genre(genre.value)
        logger.debug(f"{theme=}")
        await send_msg.edit(content=f"{p_bar.print('テーマ選定 done...')}")

        quiz.title = quiz.get_title(theme)
        quiz.title_near = quiz.get_title_near(theme, quiz.title)
        await send_msg.edit(content=f"{p_bar.print('タイトル選定 done...')}")

        quiz.input_txt = quiz.get_txt(quiz.title)
        quiz.categories = quiz.get_categories(quiz.title)
        quiz.noun_dict = quiz.get_topk_noun(quiz.input_txt)
        await send_msg.edit(content=f"{p_bar.print('ヒント生成 done...')}")

        quiz.summary = quiz.get_summary(quiz.title)
        quiz.images = quiz.get_images(quiz.title)
        await send_msg.edit(content=f"{p_bar.print('大ヒント生成 done...')}")

    except BaseException as e:
        await channel.send(f"エラーが発生したぞ！\n{e}")
        return
    time.sleep(1)

    await channel.send(f"じゃあ始めるぜ...{genre.name}\n----------------------------------\n")

    for i in range(quiz.NUM_MAX_HINT):
        # len(quiz.title) x 〇 の文字列を表示する
        if i == quiz.NUM_MAX_HINT // 4:
            await channel.send(f"ヒント：{quiz.get_masked_title('')}")
        if i == quiz.NUM_MAX_HINT * 1 // 2:
            part_title = quiz.get_part_of_title(0.25)
            await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")
        if i == quiz.NUM_MAX_HINT * 3 // 4:
            part_title = quiz.get_part_of_title(0.5)
            await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")
        if i == quiz.NUM_MAX_HINT * 1 // 4:
            if quiz.exist_hint_image:
                txt, path_to_file = quiz.get_image()
                if path_to_file != "":
                    await channel.send(f"{txt}", file=discord.File(path_to_file))
        if quiz.already_answered:
            break
        time.sleep(1)
        msg = f"{i+1}/{quiz.NUM_MAX_HINT}: "
        if quiz.exist_hint("LOW"):
            await channel.send(f"{msg}{quiz.get_hint('LOW')}")
            continue
        if quiz.exist_hint("HIGH"):
            await channel.send(f"{msg}{quiz.get_hint('HIGH')}")
            continue

    wait(5)
    if not quiz.already_answered:
        await channel.send(f"### 大ヒント！\n{quiz.summary}")

    wait(5)
    if not quiz.already_answered:
        part_title = quiz.get_part_of_title(0.75)
        await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")

    wait(10)
    await channel.send(f"正解は**{quiz.get_answer()}**だ！\n{quiz.get_answer_url()}")


@client.tree.command(
    name="quiz",
    description="連想されるキーワードを当ててくれ!",
)
@app_commands.describe(
    theme="好きなテーマを単語で入力してくれ！",
)
async def quiz_morgana(interaction: discord.Interaction, theme: str) -> None:
    """クイズを出題する関数"""
    from quiz import Quiz
    import time
    global quiz

    if not interaction.channel_id in [int(config["DISCORD_CHANNEL_ID_QUIZ"]), int(config["DISCORD_CHANNEL_ID_QUIZ_DEBUG"])]:
        await interaction.response.send_message(f"このチャンネルでは無効だ！")
        return

    # use singleton pattern, global quiz object is singleton
    if "quiz" in globals() and not quiz.force_answer:
        await interaction.response.send_message(f"クイズは既に進行中だ！")
        return

    channel = client.get_channel(interaction.channel_id)
    p_bar = ProgressBar(total=4)
    msg = f"テーマは{theme}だな！"
    await interaction.response.send_message(f"{p_bar.print(msg)}")
    send_msg = await interaction.original_response()

    try:
        quiz = Quiz(NUM_MAX_HINT=20)
        # quiz.setup_quiz(theme)
        quiz.title = quiz.get_title(theme)
        quiz.title_near = quiz.get_title_near(theme, quiz.title)
        await send_msg.edit(content=f"{p_bar.print('タイトル選定 done...')}")

        quiz.input_txt = quiz.get_txt(quiz.title)
        quiz.categories = quiz.get_categories(quiz.title)
        quiz.noun_dict = quiz.get_topk_noun(quiz.input_txt)
        await send_msg.edit(content=f"{p_bar.print('ヒント生成 done...')}")

        quiz.summary = quiz.get_summary(quiz.title)
        quiz.init_hint()
        quiz.images = quiz.get_images(quiz.title)
        await send_msg.edit(content=f"{p_bar.print('大ヒント生成 done...')}")

    except BaseException as e:
        await channel.send(f"エラーが発生したぞ！\n{e}")
        return
    time.sleep(1)

    await channel.send(f"じゃあ始めるぜ...{theme}\n----------------------------------\n")

    for i in range(quiz.NUM_MAX_HINT):
        if i == quiz.NUM_MAX_HINT // 4:
            # len(quiz.title) x 〇 の文字列を表示する
            await channel.send(f"ヒント：{quiz.get_masked_title('')}")
        if i == quiz.NUM_MAX_HINT * 1 // 2:
            part_title = quiz.get_part_of_title(0.25)
            await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")
        if i == quiz.NUM_MAX_HINT * 1 // 2:
            if quiz.exist_hint_image:
                txt, path_to_file = quiz.get_image()
                if path_to_file != "":
                    await channel.send(f"{txt}", file=discord.File(path_to_file))
        if i == quiz.NUM_MAX_HINT * 3 // 4:
            part_title = quiz.get_part_of_title(0.5)
            await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")
        if quiz.already_answered:
            break
        time.sleep(1)
        msg = f"{i+1}/{quiz.NUM_MAX_HINT}: "
        if quiz.exist_hint("LOW"):
            await channel.send(f"{msg}{quiz.get_hint('LOW')}")
            continue
        if quiz.exist_hint("HIGH"):
            await channel.send(f"{msg}{quiz.get_hint('HIGH')}")
            continue

    wait(5)
    if not quiz.already_answered:
        await channel.send(f"### 大ヒント！\n{quiz.summary}")

    wait(5)
    if not quiz.already_answered:
        part_title = quiz.get_part_of_title(0.75)
        await channel.send(f"ヒント：{quiz.get_masked_title(part_title)}")

    wait(10)
    await channel.send(f"正解は**{quiz.get_answer()}**だ！\n{quiz.get_answer_url()}")

    # clear cache until next quiz
    del quiz

if config["token"] is None:
    logger.error("token is None.")
    sys.exit(1)
else:
    client.run(config["token"])

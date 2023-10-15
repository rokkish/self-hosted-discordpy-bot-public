import datetime
import logging
import json
import requests
import random

from bs4 import BeautifulSoup
import discord
from discord.ext import tasks
from dotenv import dotenv_values
import tweepy

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


x_client = tweepy.Client(
    bearer_token=x_bearer_token,
    consumer_key=x_api_key,
    consumer_secret=x_api_key_secret,
    access_token=x_access_token,
    access_token_secret=x_access_token_secret,
)

@tasks.loop(minutes=1)
async def loop():
    now = datetime.datetime.now().strftime("%H:%M")
    # print(f"loop {now=}")

    # start of day, end of day
    # if now == "09:00" or now == "18:00":
    #     await daily_steam_news()

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await loop.start()

async def daily_steam_news():
    channel = client.get_channel(int(config["DISCORD_CHANNEL_ID_GAME"]))
    url = "https://store.steampowered.com/curator/29024848-Indie-Freaks-in-Japan/"
    r = requests.get(
        url=url,
        timeout=10,
        allow_redirects=False,
    )
    if channel is None or r.status_code != 200:
        await channel.send(f"ワガハイとしたことが...")
    else:
        soup = BeautifulSoup(r.text, "html.parser")
        # print(soup.prettify())
        recommendation_desc = soup.find_all("div", class_="recommendation_desc")
        recommendation_link = soup.find_all("a", class_="recommendation_link")
        curator_review_date = soup.find_all("span", class_="curator_review_date")
        recommendation_image = soup.find_all("div", class_="capsule smallcapsule")
        # curator_review_date is "27 September" format %d %B
        today = datetime.datetime.now().strftime("%d")
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d")
        ret = []
        for i, (desc, link, date, image) in enumerate(zip(recommendation_desc, recommendation_link, curator_review_date, recommendation_image)):
            # 桁数があっていないため、正しく判定ができていなかったため、桁数を揃える
            # today='04'
            # yesterday='03'
            # date.text='4 October'
            review_date = f"{date.text.split(' ')[0]}"
            review_date = f"{int(review_date):0=2}"
            print(f"{review_date=}")
            if today != review_date and yesterday != review_date:
                continue
            desc_ = desc.text.replace("\t", "")
            date_ = date.text.replace("\t", "")
            # ret.append(f'{i}:\n{desc_}\n{date_}\n{link["href"]}')
            ret.append({
                "desc": desc_,
                "date": date_,
                "link": link["href"],
                "image": image.find('img').get('src'),
            })

        # no news
        if len(ret) == 0:
            return None
            msg_no_news = random.choice([
                "0件だと！？ワガハイとしたことが……\n",
                "むむ！？\n",
                "あれ！？\n",
                "おっと失敬！\n",
                "何だと！？\n",
                "抜かったか･･･\n",
                "うっ･･･これはいかんな･･･\n",
                "ふ、不覚･･･だ･･･\n",
                "ぐっ･･･すまぬ･･･\n",
                " Indie Freaks ！？ 返事をしろぉぉぉ！\n",
            ])
            ret.append(msg_no_news)

        # choices from https://wikiwiki.jp/pq2/%E5%8F%B0%E8%A9%9E%E9%9B%86/%E3%83%A2%E3%83%AB%E3%82%AC%E3%83%8A
        msg = random.choice([
            "ここで Indie Freaks だー！\n",
            "Indie Freaks の証を見よ！\n",
            "Indie Freaks の出番だ！\n",
            "おいオタカラ…じゃない！レアなゲームがあるぜ！\n",
            "威を示せ、 Indie Freaks ー！\n",
            "引導を渡す、Indie Freaks ー！\n",
            "フッフッフー！ついに Indie Freaks の時代が来たなー！\n",
            "Indie Freaks 、頼んだぜ！\n",
            "やるな Indie Freaks の奴。ワガハイも負けてられねえぜ！\n",
            "おお！これは、もしや…！？\n",
            "むっ、初めて見るゲームだ。弱点を見つけて一網打尽にするぞ！\n",
            "ほいっとな！\n",
            "これでもどうぞ！\n",
            "そーら！\n",
            "はい！\n",
            "どっこらしょ！\n",
            "来れ、我が半身！\n",
        ])
        await channel.send(f'{msg}')

        # send news
        for msg in ret:
            # await channel.send(f"{msg}")
            embed = discord.Embed(title="Steam", description=msg["desc"])
            embed.add_field(name="date", value=msg["date"], inline=False)
            embed.add_field(name="link", value=f"[steam link](<{msg['link']}>)")
            embed.set_image(url=msg["image"])
            await channel.send(embed=embed)
            # break # 1 news only

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

    if message.content.startswith("$get_x"):
        await message.channel.send("Getting tweets from list...")
        tweets = x_client.get_list_tweets(id=1707017898122989705, max_results=3)
        # free plan cannot use this API, basic plan (100$ / month) can use this API...
        for tweet in tweets.data:
            await message.channel.send(tweet.text)

    if message.content.startswith("フェルン"):
        await message.channel.send("", file=discord.File("./.image_cache/fern.jpg"))
    if message.content.startswith("ずる") or message.content.startswith("ズル"):
        await message.channel.send("", file=discord.File("./.image_cache/fern_zuru.jpg"))
    if message.content.startswith("イタチャイ"):
        await message.channel.send("", file=discord.File("./.image_cache/itachay.png"))
    if message.content.startswith("何も"):
        await message.channel.send("", file=discord.File("./.image_cache/zoro_nothing.png"))

    # get latest info from url with requests
    if message.content.startswith("$mor_st_curator"):
        url = "https://store.steampowered.com/curator/29024848-Indie-Freaks-in-Japan/"
        r = requests.get(
            url=url,
            timeout=10,
            allow_redirects=False,
        )
        # choices from https://wikiwiki.jp/pq2/%E5%8F%B0%E8%A9%9E%E9%9B%86/%E3%83%A2%E3%83%AB%E3%82%AC%E3%83%8A
        msg = random.choice([
            "ここで Indie Freaks だー！\n",
        ])
        await message.channel.send(f'{msg}')

        soup = BeautifulSoup(r.text, "html.parser")
        print(soup.prettify())
        # await message.channel.send(f'[debug] {soup.prettify()}')
        recommendation_desc = soup.find_all("div", class_="recommendation_desc")
        recommendation_link = soup.find_all("a", class_="recommendation_link")
        curator_review_date = soup.find_all("span", class_="curator_review_date")
        recommendation_image = soup.find_all("div", class_="capsule smallcapsule")
        # curator_review_date is "27 September" format %d %B
        today = datetime.datetime.now().strftime("%d")
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d")
        print(f"{today=}")
        print(f"{yesterday=}")
        ret = []
        ret_new = []
        for i, (desc, link, date, image) in enumerate(zip(recommendation_desc, recommendation_link, curator_review_date, recommendation_image)):
            r_game = requests.get(
                url=link["href"],
                timeout=10,
                allow_redirects=False,
            )
            soup_game = BeautifulSoup(r_game.text, "html.parser")
            movie = "none"
            for item in soup_game.find_all('div', class_="highlight_player_item highlight_movie"):
                movie = item.get("data-mp4-hd-source")
            # 桁数があっていないため、正しく判定ができていなかったため、桁数を揃える
            # today='04' # yesterday='03' # date.text='4 October'
            review_date = f"{date.text.split(' ')[0]}"
            review_date = f"{int(review_date):0=2}"
            print(f"{review_date=}")
            if today != review_date and yesterday != review_date:
                # continue
                pass
            desc_ = desc.text.replace("\t", "")
            date_ = date.text.replace("\t", "")
            ret.append(f'{i}:\n{desc_}\n[{date_}]({link["href"]})')
            ret_new.append({
                "desc": desc_,
                "date": date_,
                "link": link["href"],
                "image": image.find('img').get('src'),
                "movie": movie,
            })

        # no news
        if len(ret) == 0:
            msg_no_news = random.choice([
                "0件だと！？ワガハイとしたことが……\n",
            ])
            ret.append(msg_no_news)

        # send news
        print(f"{ret=}")
        print(f"{ret_new=}")
        for msg_new in ret_new:
            # await message.channel.send(f"{msg}")
            # print(f"{msg_new=}")
            embed = discord.Embed(title="Steam", description=msg_new["desc"])
            embed.add_field(name="date", value=msg_new["date"], inline=False)
            embed.add_field(name="link", value=f"[steam link](<{msg_new['link']}>)")
            embed.set_image(url=msg_new["image"])
            await message.channel.send(embed=embed)
            # embed.add_field(name="movie", value=msg_new["movie"], inline=False)
            await message.channel.send(f"[movie]({msg_new['movie']})")
            break # 1 news only

    if message.content.startswith("$mor_steam"):
        headers = {
            "x-webapi-key": config["STEAM_WEB_API_KEY"],
        }
        url = f"https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/?steamid={STEAM_MY_UID}&appid=440&count=3&maxlength=300&format=json"
        r = requests.get(
            url=url,
            headers=headers,
            timeout=10,
            allow_redirects=False,
        )
        if r.status_code == 200:
            print(r.status_code)
            print(r.headers["content-type"])
            print(r.encoding)
            print(json.loads(r.text))
            await message.channel.send(f"{json.loads(r.text)['appnews']['newsitems'][0]['contents']}")
        else:
            await message.channel.send(f"fetch error {r.status_code=}")

    if message.content.startswith("これドクターストーン最新話です。"):
        await message.add_reaction("👀")
        await message.channel.send("https://www.netflix.com/browse?jbv=81046193")

# logger.info(config['token'])
client.run(config["token"])

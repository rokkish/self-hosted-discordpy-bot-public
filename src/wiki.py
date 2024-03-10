import aiohttp
from PIL import Image
from io import BytesIO
import wikipedia
from parsel import Selector
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("morgana").getChild(__name__)

# wikipedia page の html から情報を抽出する parser クラス
class WikiParser:
    def __init__(self, page_name: str = None, prefix_html_file: str = "html/"):
        self.page = None
        self.page_name = page_name
        self.prefix_file = prefix_html_file
        self.page_html = None
        self.selector = None
        self.page_indexs = []
        self.urls_thumbnail = []
        if not Path(f"{self.prefix_file}").exists():
            Path(f"{self.prefix_file}").mkdir(parents=True, exist_ok=True)

    def set_page(self) -> None:
        wikipedia.set_lang("ja")
        try:
            self.page = wikipedia.page(self.page_name)
            logger.info("wikipedia Got page")
        except wikipedia.exceptions.DisambiguationError as e:
            logger.error(f"DisambiguationError: {e}")
        except wikipedia.exceptions.PageError:
            logger.error(f"PageError: {self.page_name} not found")

    def set_html(self):
        # if saved file exists, load it
        try:
            with open(f"{self.page_name}.html", "r") as f:
                self.page_html = f.read()
        except FileNotFoundError:
            if self.page is None:
                self.set_page()
            self.page_html = self.page.html()
            # save html
            with open(f"{self.prefix_file}{self.page_name}.html", "w") as f:
                f.write(self.page_html)

    def feed_indexs(self):
        self.selector = Selector(text=self.page_html)
        # index on wikipedia, select class=toctext
        for section in self.selector.xpath("//div/ul/li/a/span[has-class('toctext')]/text()"):
            sec = section.get()
            if type(sec) is str:
                self.page_indexs.append(sec)
    def feed_thumbnails(self):
        self.selector = Selector(text=self.page_html)
        # thumnails on wikipedia, select /a/img/src in figure[@typeof='mw:File/Thumb']
        for img in self.selector.xpath("//figure[@typeof='mw:File/Thumb']/a/img/@src"):
            img_url = img.get()
            if type(img_url) is str:
                self.urls_thumbnail.append(img_url)
    async def fetch_image(self, url: str) -> Optional[str]:
        # response = requests.get(f"https:{url}")
        async def fetch(url: str):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.read()
        response = await fetch(f"https:{url}")
        try:
            img = Image.open(BytesIO(response.content))
        except BaseException as e:
            logger.error(f"Error: {e}")
            return None
        path = f"{self.prefix_file}{self.page_name}.png"
        img.save(f"{path}")
        return path
    def update_archived_indexs(self):
        # save index as json like {"page_name": index, ...}
        # load index.json and update it
        j = {}
        try:
            with open(f"{self.prefix_file}index.json", "r", encoding="utf-8") as f:
                j = json.load(f)
            if not self.page_name in j.keys():
                j[self.page_name] = self.page_indexs
        except FileNotFoundError:
            j = {self.page_name: self.page_indexs}
        with open(f"{self.prefix_file}index.json", "w", encoding="utf-8") as f:
            # 日本語文字化け対策
            json.dump(j, f, ensure_ascii=False, indent=4)
        
    def get_index(self):
        return self.page_indexs
    def get_thumbnails(self):
        return self.urls_thumbnail

def main(page_name: str, prefix="./"):
    parser = WikiParser(page_name, prefix)
    parser.set_html()
    parser.feed_indexs()
    parser.update_archived_indexs()
    parser.feed_thumbnails()
    print(f"{parser.get_index()=}")
    print(f"{parser.get_thumbnails()=}")

if __name__ == "__main__":
    import sys
    main(sys.argv[1])

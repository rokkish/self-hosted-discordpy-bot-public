import requests
from PIL import Image
from io import BytesIO
import wikipedia
from parsel import Selector
import json
import logging
from pathlib import Path

logger = logging.getLogger("morgana").getChild(__name__)

# wikipedia page の html から情報を抽出する parser クラス
class WikiParser:
    def __init__(self, page_name: str = None, prefix_html_file: str = "html/"):
        self.page_name = page_name
        self.prefix_file = prefix_html_file
        self.page_html = None
        self.selector = None
        self.page_indexs = []
        self.urls_thumbnail = []
        if not Path(f"{self.prefix_file}").exists():
            Path(f"{self.prefix_file}").mkdir(parents=True, exist_ok=True)

    def set_html(self, page: wikipedia.WikipediaPage = None):
        # if saved file exists, load it
        try:
            with open(f"{self.page_name}.html", "r") as f:
                self.page_html = f.read()
        except FileNotFoundError:
            wikipedia.set_lang("ja")
            if page is not None:
                self.page_html = page.html()
            else:
                page = wikipedia.page(self.page_name)
            self.page_html = page.html()
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
    def fetch_image(self, url: str) -> str:
        response = requests.get(f"https:{url}")
        img = Image.open(BytesIO(response.content))
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

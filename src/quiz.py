import re
import MeCab
import random
import collections
import wikipedia
import logging
from typing import Tuple


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# set color format
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
# set stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# wikipedia の title を当てるゲームを管理するクラス
class Quiz():
    def __init__(self, /, NUM_MAX_HINT=30):
        super().__init__()
        self.search_themes = [
            "onepiece",
            "dr.stone",
            "ハンターハンター",
            "刃牙",
            "龍が如く",
            "鬼滅の刃",
            "ワンパンマン",
            "進撃の巨人",
            "ジョジョの奇妙な冒険",
            "声優",
            "アニメ",
            "漫画",
            "ゲーム",
            "アイドル",
            "映画",
            "音楽",
        ]
        self.title = ""
        self.title_near: list[str] = []
        self.summary = ""
        self.input_txt = ""
        self.categories: list[str] = []
        self.images: list[str] = []  # url of images
        self.noun_dict = {"HIGH": [], "LOW": []}
        self.maintanance = False
        self.MIN_HINT_WORD_LEN = 2
        self.NUM_MAX_HINT = NUM_MAX_HINT
        self.NUM_SEARCH = 20
        self.NUM_HIGH_HINT = 5
        self.already_answered = False
        self.force_answer = False  # 強制的に回答を表示したかどうか 

    def get_themes(self) -> list:
        return self.search_themes

    def setup_quiz(self, search_theme: str):
        self.title = self.get_title(search_theme)
        self.title_near = self.get_title_near(search_theme, self.title)
        self.summary = self.get_summary(self.title)
        self.input_txt = self.get_txt(self.title)
        self.categories = self.get_categories(self.title)
        self.noun_dict = self.get_topk_noun(self.input_txt)

    def get_title_near(self, search_theme: str, title: str) -> list:
        no_theme = self.__remove_theme(search_theme, title)
        no_space = self.__remove_space(no_theme)
        no_symbol = self.__remove_symbol(no_space)
        return [
            no_theme,
            no_space,
            no_symbol,
        ]

    def __remove_theme(self, search_theme: str, title: str) -> str:
        search_theme = self.__remove_space(search_theme)
        search_theme = self.__remove_txt_in_symbol(search_theme)
        search_theme = self.__remove_symbol(search_theme)
        title = self.__remove_space(title)
        title = self.__remove_txt_in_symbol(title)
        title = self.__remove_symbol(title)
        return re.sub(search_theme, "", title).lower()
    def __remove_space(self, inp: str) -> str:
        return re.sub(r"\s", "", inp).lower()
    def __remove_txt_in_symbol(self, inp: str) -> str:
        return re.sub(r"（.*?）|\(.*?\)", "", inp).lower()
    def __remove_symbol(self, inp: str) -> str:
        return re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]').sub("", inp).lower()

    def get_title(self, search_theme: str) -> str:
        """title を設定する関数"""
        # q. prompt:Wikipedia の title をランダムに設定する関数を定義したい
        wikipedia.set_lang("ja")
        title_candidates = wikipedia.search(search_theme, results=self.NUM_SEARCH)
        logger.debug("wikipedia Searched...")
        # cut candidates lengh of str over 10
        title_candidates = [x for x in title_candidates if len(x) < 10]
        if len(title_candidates) == 0:
            raise Exception("No title candidates under 10 char")
        # cut candidates that include search_theme
        title_candidates = [x for x in title_candidates if search_theme != x]
        if len(title_candidates) == 0:
            raise Exception("No title candidates")

        title = random.choice(title_candidates)
        return title

    def get_summary(self, title: str) -> str:
        summary = wikipedia.summary(title)
        logger.debug("wikipedia Got summary...")
        # summary から title とカッコ内の文字列(読み仮名、英語表記）を削除
        replaced_title = "〇"*len(title)
        summary = self.__remove_space(summary)
        summary = re.sub(f"{title}"+r"（.*?）", replaced_title, summary)
        summary = re.sub(f"{title}"+r"\(.*?\)", replaced_title, summary)
        summary = re.sub(f"{title}", replaced_title, summary)
        # # title を１文字に分解して、summary から削除
        # try:
        #     for char in set(title):
        #         logging.debug(f"char: {char}")
        #         summary = re.sub(char, "Z", summary)
        # except Exception as e:
        #     logging.error(e)
        # finally:
        return summary

    def is_correct(self, answer: str) -> bool:
        """回答が正しいかどうかを判定する関数"""
        ans = answer.lower()
        title = self.title.lower()
        return ans in [title, *self.title_near]

    # 回答が惜しいかどうかを判定する関数
    def is_close(self, answer: str) -> bool:
        if len(answer) < 2:
            return False
        return answer in self.title

    # 正解の一部をマスクするための部分文字列を返す関数
    def get_part_of_title(self, open_rate: float) -> str:
        if open_rate < 0 or open_rate > 1:
            return "(error)"
        open_len = int(len(self.title) * open_rate)
        if open_len == len(self.title):
            open_len -= 1
        return self.title[:open_len]

    # 回答がヒットした文字列は返すが、それ以外はマスクする
    def get_masked_title(self, answer: str) -> str:
        tmp = self.title
        try:
            tmp2 = tmp
            for char in set(tmp2):
                if char == "(" or char == ")":
                    continue
                if not char in answer:
                    tmp = re.sub(f"{char}", "〇", tmp)
        except Exception as e:
            logging.error(e)
            return "(error)"
        return tmp

    def update_answered(self):
        self.already_answered = True

    def get_txt(self, title: str) -> str:
        """title から Wikipedia の記事の文字列を取得する関数
        """
        if self.input_txt != "":
            return self.input_txt
        # q. prompt:Wikipedia の記事の文字列を取得する関数を定義したい
        # a. 以下のように定義することで、Wikipedia の記事の文字列を取得する関数を定義できます。
        # 1. wikipedia をインポート
        # 2. wikipedia.page()でWikipediaの記事を取得
        # 3. Wikipediaの記事の文字列を取得
        wikipedia.set_lang("ja")
        try:
            txt = wikipedia.page(title).content
            logger.debug("wikipedia Got page")
            return txt
        except wikipedia.exceptions.DisambiguationError as e:
            return e
        except wikipedia.exceptions.PageError:
            return ""

    def get_images(self, title: str) -> list:
        """title から Wikipedia の記事の画像を取得する関数
        """
        wikipedia.set_lang("ja")
        try:
            images = wikipedia.page(title).images
            # drop UI_icon_edit
            images = [i for i in images if not "UI_icon_edit" in i]
            return images
        except wikipedia.exceptions.DisambiguationError as e:
            return []
        except wikipedia.exceptions.PageError:
            return []
    def get_categories(self, title: str) -> list:
        """title から Wikipedia の記事のカテゴリを取得する関数
        """
        wikipedia.set_lang("ja")
        try:
            categories = wikipedia.page(title).categories
            return categories
        except wikipedia.exceptions.DisambiguationError as e:
            return []
        except wikipedia.exceptions.PageError:
            return []

    def get_topk_noun(self, input_txt: str) -> dict:
        """出現頻度の高い名詞リストを返す関数
        """
        # q. prompt:ランダムな名詞を返す関数を定義したい
        # a. 以下のように定義することで、ランダムな名詞を返す関数を定義できます。
        # 1. MeCab.Tagger()をインスタンス化
        # 2. parse()で形態素解析
        # 3. 名詞のリストを作成
        # 4. 出現頻度を算出し、出現頻度の高い順に並べ替え
        tagger = MeCab.Tagger()
        parsed = tagger.parse(input_txt)
        logger.debug("Mecab parsed!")
        nouns = [line.split("\t")[0] for line in parsed.split("\n") if "名詞" in line]
        # ヒントとして無効な文字列を削除する
        nouns = [noun for noun in nouns if len(noun) > self.MIN_HINT_WORD_LEN]
        # 記号を削除する
        nouns = [noun for noun in nouns if not noun.isascii()]
        # 数字を削除する
        nouns = [noun for noun in nouns if not noun.isdigit()]
        nouns_list = collections.Counter(nouns).most_common(self.NUM_MAX_HINT)
        # ヒントのランク設定
        noun_dict = {}
        noun_dict["HIGH"] = [noun for noun, _ in nouns_list[:self.NUM_HIGH_HINT]]
        noun_dict["LOW"] = [noun for noun, _ in nouns_list[self.NUM_HIGH_HINT:]]
        return noun_dict

    # 残りのヒント数
    def remain_hint(self, strength: str) -> int:
        return len(self.noun_dict[strength])
    def all_remain_hint(self) -> str:
        return f"HIGH: {len(self.noun_dict['HIGH'])}\nLOW: {len(self.noun_dict['LOW'])}\n"

    def exist_hint(self, strength: str) -> bool:
        """ヒントが存在するかどうかを判定する関数
        """
        return len(self.noun_dict[strength]) > 0

    def exist_hint_image(self) -> bool:
        return len(self.images) > 0

    def get_hint(self, strength: str) -> str:
        """ヒントを返す関数
        """
        # choice random and remove it from list
        if not self.exist_hint(strength):
            return "もうヒントはありません"
        h = random.choice(self.noun_dict[strength])
        self.noun_dict[strength].remove(h)
        return h

    def get_image(self) -> Tuple[str, str]:
        import requests
        import tempfile
        from PIL import Image
        from io import BytesIO
        def _load_image(url: str) -> str:
            response = requests.get(url, stream=True)
            response.raw.decode_content = True
            if "jpg" in url:
                img = Image.open(BytesIO(response.content))
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                    img.save(f, "JPEG")
                    return f.name
            elif "svg" in url:
                # svg を jpeg として保存する with cairosvg
                import cairosvg
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                    cairosvg.svg2png(bytestring=response.content, write_to=f.name)
                    return f.name
            return ""
      
        if len(self.images) == 0:
            return ("画像ヒントはありません", "")
        i = random.choice(self.images)
        self.images.remove(i)
        path_to_tmp_img = _load_image(i)
        return ("画像ヒント", path_to_tmp_img)

    def get_category(self) -> str:
        if len(self.categories) == 0:
            return "もうカテゴリヒントはありません"
        c = random.choice(self.categories)
        self.categories.remove(c)
        return c

    def get_answer(self) -> str:
        return self.title

    def get_answer_url(self) -> str:
        return wikipedia.page(self.title).url

    def __test__scenario_solid_theme(self):
        self.setup_quiz("onepiece")
        # print(f"{self.title=}")
        # print(f"{self.summary=}")
        # print(f"{self.input_txt[:100]=}")
        # print(f"{self.noun_dict=}")
        # print(f"{self.is_correct(self.title)=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('HIGH')=}")
    def __test__scenario_auto_theme(self):
        theme = random.choice(self.search_themes)
        self.setup_quiz(theme)
        # print(f"{self.title=}")
        # print(f"{self.summary=}")
        # print(f"{self.input_txt[:100]=}")
        # print(f"{self.noun_dict=}")
        # print(f"{self.is_correct(self.title)=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('HIGH')=}")
    def __test__scenario_input_theme(self, theme: str):
        self.setup_quiz(theme)
        # print(f"{self.title=}")
        # print(f"{self.summary=}")
        # print(f"{self.input_txt[:100]=}")
        # print(f"{self.noun_dict=}")
        # print(f"{self.is_correct(self.title)=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('HIGH')=}")

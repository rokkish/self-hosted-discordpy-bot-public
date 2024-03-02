import re
import MeCab
import random
import collections
import wikipedia
import logging

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
    def __init__(self):
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
        self.title_no_symbol = ""
        self.title_no_theme = ""
        self.summary = ""
        self.input_txt = ""
        self.noun_list = {"HIGH": [], "LOW": []}
        self.maintanance = False
        self.MIN_HINT_WORD_LEN = 2
        self.NUM_MAX_HINT = 30
        self.NUM_HIGH_HINT = 5
        self.already_answered = False

    def get_themes(self) -> list:
        return self.search_themes

    def setup_quiz(self, search_theme: str):
        self.title = self.get_title(search_theme)
        no_space = re.sub(r"\s", "", self.title)
        self.title_no_symbol = re.compile('[!"#$%&\'\\\\()*+,-./:;<=>?@[\\]^_`{|}~「」〔〕“”〈〉『』【】＆＊・（）＄＃＠。、？！｀＋￥％]').sub("", no_space)
        self.title_no_theme = re.sub(search_theme, "", self.title)
        self.summary = self.get_summary(self.title)
        self.input_txt = self.get_txt(self.title)
        bare_noun_list = self.get_topk_noun(self.input_txt)
        self.noun_list["HIGH"] = [noun for noun, _ in bare_noun_list[:self.NUM_HIGH_HINT]]
        self.noun_list["LOW"] = [noun for noun, _ in bare_noun_list[self.NUM_HIGH_HINT:]]

    def get_title(self, search_theme: str) -> str:
        """title を設定する関数"""
        # q. prompt:Wikipedia の title をランダムに設定する関数を定義したい
        wikipedia.set_lang("ja")
        title_candidates = wikipedia.search(search_theme, results=20)
        logger.debug("wikipedia Searched...")
        # cut candidates lengh of str over 10
        title_candidates = [x for x in title_candidates if len(x) < 10]
        # cut candidates that include search_theme
        title_candidates = [x for x in title_candidates if search_theme != x]
        if len(title_candidates) == 0:
            raise Exception("No title candidates")

        while True:
            title = random.choice(title_candidates)
            if title != search_theme:
                break
        return title

    def get_summary(self, title: str) -> str:
        summary = wikipedia.summary(title)
        logger.debug("wikipedia Got summary...")
        # summary から title とカッコ内の文字列(読み仮名、英語表記）を削除
        summary = re.sub(f"{title}", "XXXX", summary)
        summary = re.sub(r"（.*）", "YYYY", summary)
        # title を１文字に分解して、summary から削除
        try:
            for char in set(title):
                logging.debug(f"char: {char}")
                summary = re.sub(char, "Z", summary)
        except Exception as e:
            logging.error(e)
        finally:
            return summary

    def is_correct(self, answer: str) -> bool:
        """回答が正しいかどうかを判定する関数"""
        ans = answer.lower()
        title = self.title.lower()
        title_no_symbol = self.title_no_symbol.lower()
        title_no_theme = self.title_no_theme.lower()
        return ans == title or ans == title_no_symbol or ans == title_no_theme

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
            return e.options
        except wikipedia.exceptions.PageError:
            return ""

    def get_topk_noun(self, input_txt: str) -> str:
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
        return nouns_list

    # 残りのヒント数
    def remain_hint(self, strength: str) -> int:
        return len(self.noun_list[strength])
    def all_remain_hint(self) -> str:
        return f"HIGH: {len(self.noun_list['HIGH'])}\nLOW: {len(self.noun_list['LOW'])}\n"

    def exist_hint(self, strength: str) -> bool:
        """ヒントが存在するかどうかを判定する関数
        """
        return len(self.noun_list[strength]) > 0

    def get_hint(self, strength: str) -> str:
        """ヒントを返す関数
        """
        # choice random and remove it from list
        if not self.exist_hint(strength):
            return "もうヒントはありません"
        h = random.choice(self.noun_list[strength])
        self.noun_list[strength].remove(h)
        return h

    def get_answer(self) -> str:
        return self.title

    def get_answer_url(self) -> str:
        return wikipedia.page(self.title).url

    def __test__scenario_solid_theme(self):
        self.setup_quiz("onepiece")
        # print(f"{self.title=}")
        # print(f"{self.summary=}")
        # print(f"{self.input_txt[:100]=}")
        # print(f"{self.noun_list=}")
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
        # print(f"{self.noun_list=}")
        # print(f"{self.is_correct(self.title)=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('HIGH')=}")
    def __test__scenario_input_theme(self, theme: str):
        self.setup_quiz(theme)
        # print(f"{self.title=}")
        # print(f"{self.summary=}")
        # print(f"{self.input_txt[:100]=}")
        # print(f"{self.noun_list=}")
        # print(f"{self.is_correct(self.title)=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('LOW')=}")
        print(f"{self.get_hint('HIGH')=}")

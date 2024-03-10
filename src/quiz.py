import re
import MeCab
import random
import collections
import wikipedia
import logging
from typing import Tuple

from quiz_genre import QuizGenresChoices
from wiki import WikiParser

logger = logging.getLogger("morgana").getChild(__name__)
# logger.setLevel(logging.DEBUG)
# Filter urillib3.connectionpool log from logger
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


class Quiz():
    """wikipedia の title を当てるゲームを管理するクラス"""
    def __init__(self, /, NUM_MAX_HINT=30, genre: str = QuizGenresChoices.ノンジャンル.name):
        super().__init__()
        self.genre = QuizGenresChoices.ノンジャンル
        self.genres_not_search = [QuizGenresChoices.都道府県.value, QuizGenresChoices.化学_理系学問.value, QuizGenresChoices.スポーツ.value]
        self.genres_not_open_hint = [QuizGenresChoices.都道府県.value]
        self.given_theme = ""
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
        self.NUM_SEARCH = 100
        self.NUM_HIGH_HINT = 5
        self.already_answered = False
        self.force_answer = False  # 強制的に回答を表示したかどうか
        self.wiki_parser = None
        self.prefix_cache_dir = ".cache/"
        self.user_created = False  # ユーザにより問題が作成されたかどうか
        self.user_name_created = ""  # ユーザ名

    def init_user_created(self, user_name: str) -> None:
        self.user_created = True
        self.user_name_created = user_name
    def is_user_created(self) -> bool:
        return self.user_created

    def init_hint(self):
        if self.title == "":
            logging.error("title is empty")
            return
        self.wiki_parser = WikiParser(self.title, self.prefix_cache_dir)
        self.wiki_parser.set_page()
        self.wiki_parser.set_html()
        self.wiki_parser.feed_indexs()
        self.wiki_parser.feed_thumbnails()
        self.wiki_parser.update_archived_indexs()

    def pick_theme_from_genre(self, genre: str) -> str:
        from quiz_genre import QuizGenres
        return random.choice(QuizGenres.themes[genre])

    def setup_quiz(self, search_theme: str):
        self.given_theme = search_theme
        self.title = self.get_title(search_theme)
        self.title_near = self.get_title_near(search_theme, self.title)
        self.summary = self.get_summary(self.title)
        self.input_txt = self.get_txt()
        self.categories = self.get_categories()
        self.noun_dict = self.get_topk_noun(self.input_txt)

    def get_title_near(self, search_theme: str, title: str, theme_is_title: bool = False) -> list:
        if theme_is_title:
            no_theme = search_theme
            no_space = self.__remove_space(search_theme)
        else:
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
        self.given_theme = search_theme
        # q. prompt:Wikipedia の title をランダムに設定する関数を定義したい
        wikipedia.set_lang("ja")
        title_candidates = wikipedia.search(search_theme, results=self.NUM_SEARCH)
        logger.info("wikipedia Searched...")
        # cut title if blacklist char
        black_list = ["一覧", "リスト", "国道"]
        title_candidates = [x for x in title_candidates if not any(bl in x for bl in black_list)]
        # cut endwith blacklist
        black_list_ends = ["市", "町", "村", "区", "国", "地方", "地域", "地区", "地", "学校"]
        title_candidates = [x for x in title_candidates if not x.endswith(tuple(black_list_ends))]
        # cut xxのsearch_theme
        title_candidates = [x for x in title_candidates if not re.match(r".+の"+f"{search_theme}", x)] 
        # cut search_themeのyy
        title_candidates = [x for x in title_candidates if not re.match(f"{search_theme}の"+r".+", x)]
        # cut n 月
        title_candidates = [x for x in title_candidates if not re.match(r"\d+月", x)]
        # cut n 月 m 日
        title_candidates = [x for x in title_candidates if not re.match(r"\d+月\d+日", x)]
        # cut n 年
        title_candidates = [x for x in title_candidates if not re.match(r"\d+年", x)]
        # cut candidates lengh of str over 10
        title_candidates = [x for x in title_candidates if len(x) < 10]
        if len(title_candidates) == 0:
            logger.info("No title candidates under 10 char")
            raise Exception("No title candidates under 10 char")
        # cut candidates that include search_theme
        title_candidates = [x for x in title_candidates if search_theme != x]
        if len(title_candidates) == 0:
            raise Exception("No title candidates")

        logger.info(f"{title_candidates=}")
        title = random.choice(title_candidates)
        return title

    def get_summary(self, title: str) -> str:
        summary = self.wiki_parser.page.summary # wikipedia.summary(title)
        logger.info("wikipedia Got summary...")
        # summary から title とカッコ内の文字列(読み仮名、英語表記）を削除
        title = title.lower()
        summary = summary.lower()
        replaced_title = "〇"*len(title)
        summary = self.__remove_space(summary)
        summary = summary.replace("『", "").replace("』", "")
        summary = summary.replace("「", "").replace("」", "")
        sub_txt = [
            f"{title}"+r"（.*?）",
            f"{title}株式会社",
            f"{title}"+r"\(.*?\)",
            f"{title}",
        ]
        sub_txt.extend(self.title_near)
        for sub in sub_txt:
            summary = re.sub(sub, replaced_title, summary)
        return summary

    def is_correct(self, answer: str) -> bool:
        """回答が正しいかどうかを判定する関数"""
        ans = answer.lower()
        title = self.title.lower()
        return ans in [title, *self.title_near]

    def is_close(self, answer: str) -> bool:
        """回答が惜しいかどうかを判定する関数"""
        if len(answer) < 2:
            return False
        return answer in self.title

    def get_part_of_title(self, open_rate: float) -> str:
        """正解の一部をマスクするための部分文字列を返す関数"""
        if open_rate < 0 or open_rate > 1:
            return "(error)"
        open_len = int(len(self.title) * open_rate)
        if open_len == len(self.title):
            open_len -= 1
        # if () in title, return hint without ()
        if "(" in self.title:
            open_len = min(open_len, int((self.title.find("(") - 1) * open_rate))
        if "（" in self.title:
            open_len = min(open_len, int((self.title.find("（") - 1) * open_rate))

        return self.title[:open_len]

    def get_masked_title(self, answer: str) -> str:
        """回答がヒットした文字列は返すが、それ以外はマスクする"""
        tmp = self.title
        try:
            tmp2 = tmp
            for char in set(tmp2):
                if char in ["(", ")", " "]:
                    continue
                if not char in answer:
                    tmp = re.sub(f"{char}", "〇", tmp)
        except Exception as e:
            logging.error(e)
            return "(error)"
        return tmp

    def update_answered(self):
        self.already_answered = True

    def get_txt(self) -> str:
        """title から Wikipedia の記事の文字列を取得する関数
        """
        if self.input_txt != "":
            return self.input_txt
        return self.wiki_parser.page.content

    async def get_images(self) -> list:
        """title から Wikipedia の記事の画像を取得する関数
        """
        url_thumbnails = self.wiki_parser.get_thumbnails()
        if len(url_thumbnails) == 0:
            return []
        local_image_paths = []
        for url in url_thumbnails:
            path = await self.wiki_parser.fetch_image(url)
            if path is not None:
                local_image_paths.append(path)
        return local_image_paths

    def get_categories(self) -> list:
        """title から Wikipedia の記事の目次を取得する関数
        """
        categories = self.wiki_parser.get_index()
        # remove blacklist item from categories
        black_list = ["概要", "脚注", "参考文献", "外部リンク", "関連項目", "出典"]
        categories = [x for x in categories if not any(bl in x for bl in black_list)]
        # mask self.title in categories
        categories = [re.sub(self.title, "〇"*len(self.title), x) for x in categories]
        return categories

    def choice_category(self) -> str:
        if len(self.categories) < 1:
            return "目次ヒントはありません"
        # choice random (no duplication) and remove it from list
        cs = random.sample(self.categories, 1)
        self.categories.remove(cs[0])
        return cs[0]

    def get_topk_noun(self, input_txt: str) -> dict:
        """出現頻度の高い名詞リストを返す関数
        """
        # q. prompt:ランダムな名詞を返す関数を定義したい
        # 1. MeCab.Tagger()をインスタンス化
        # 2. parse()で形態素解析
        # 3. 名詞のリストを作成
        # 4. 出現頻度を算出し、出現頻度の高い順に並べ替え
        tagger = MeCab.Tagger()
        parsed = tagger.parse(input_txt)
        logger.info("Mecab parsed!")
        nouns = [line.split("\t")[0] for line in parsed.split("\n") if "名詞" in line]
        # nouns_uniq = [line.split("\t")[0] for line in parsed.split("\n") if "固有名詞" in line]
        # ヒントとして無効な文字列を削除する
        nouns = [noun for noun in nouns if len(noun) > self.MIN_HINT_WORD_LEN]
        # ヒントとして情報量がない文字列を blacklist で削除する
        nouns = [noun for noun in nouns if not noun in ["それぞれ", "その後", "こと", "もの", "とき", "ため", "ここ", "それ", "これ", "それ", "もの", "ここ", "こちら", "そちら", "あちら", "どちら", "どれ", "どこ", "だれ", "なに", "なん", "何", "何か", "何も", "何"]]
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

    def remain_hint(self, strength: str) -> int:
        """残りのヒント数"""
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
        if h == self.title:
            return "(答えと同じためヒントを表示できません)"
        h_no_symbol = self.__remove_symbol(h)
        if len(h_no_symbol) == 0:
            logger.info(f"記号のみのためヒントを表示できません: {h_no_symbol=}")
            return "(記号のみのためヒントを表示できません)"
        return h

    def get_image(self) -> Tuple[str, str]:
        import requests
        import tempfile
        from PIL import Image
        from io import BytesIO
        def _load_image_on_page(url: str) -> str:
            response = requests.get(url, stream=True)
            if response.status_code != 200:
                return ""
            response.raw.decode_content = True
            if "jpg" in url:
                try:
                    img = Image.open(BytesIO(response.content))
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as f:
                        w, h = img.size
                        # if too small image, dont return it
                        if w < 100 or h < 100:
                            return ""
                        aspect = w / h
                        new_w = 200
                        new_h = int(new_w / aspect)
                        img.resize((new_w, new_h))
                        img.save(f, "JPEG")
                        return f.name
                except Exception as e:
                    logger.error(e)
                    return ""
            elif "svg" in url:
                # svg を jpeg として保存する with cairosvg
                import cairosvg
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f:
                    try:
                        cairosvg.svg2png(bytestring=response.content, write_to=f.name)
                    except Exception as e:
                        logger.error(e)
                        return ""
                    return f.name
            return ""
      
        if len(self.images) == 0:
            return ("画像ヒントはありません", "")
        i = random.choice(self.images)
        self.images.remove(i)
        path_to_tmp_img = i  # return local image path
        return ("画像ヒント", path_to_tmp_img)

    def get_answer(self) -> str:
        return self.title

    def get_answer_url(self) -> str:
        return self.wiki_parser.page.url

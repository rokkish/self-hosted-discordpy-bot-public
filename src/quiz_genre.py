import enum
from typing import List, Optional, Dict


class QuizGenresChoices(enum.Enum):
    ノンジャンル = "non_genre"
    アニメ漫画 = "anime_manga"
    ゲーム = "game"
    映画 = "movie"
    スポーツ = "sports"
    料理_洋服_ライフスタイル = "lifestyle"
    化学_理系学問 = "science"
    歴史_文系学問 = "history_humanity"
    都道府県 = "prefectures"

class QuizGenres(object):
    themes: Dict[str, Optional[List]] = {
        "non_genre": [
            "情報",
            "データ",
            "テクノロジー",
            "インターネット",
            "ウェブサイト",
            "ソーシャルメディア",
            "コンピュータ",
            "ソフトウェア",
            "ハードウェア",
            "アプリケーション",
            "プログラミング",
            "アルゴリズム",
            "デザイン",
            "インターフェース",
            "デジタル",
            "ネットワーク",
            "クラウド",
            "セキュリティ",
            "モバイル",
            "電子メール",
            "携帯電話",
            "スマートフォン",
            "タブレット",
            "コミュニケーション",
            "メッセージング",
            "ビジネス",
            "経済",
            "マーケティング",
            "広告",
            "ブランディング",
            "消費者",
            "販売",
            "サービス",
            "製品",
            "ユーザー",
            "エンターテインメント",
            "音楽",
            "映画",
            "テレビ",
            "ゲーム",
            "アート",
            "クリエイティビティ",
            "芸術",
            "文化",
            "スポーツ",
            "健康",
            "医療",
            "教育",
            "学習",
            "環境",
            "持続可能性",
        ],
        "anime_manga": [
            "onepiece",
            "dr.stone",
            "ハンターハンター",
            "刃牙",
            "龍が如く",
            "鬼滅の刃",
            "ワンパンマン",
            "進撃の巨人",
            "ジョジョの奇妙な冒険",
        ],
        "game": [
            "スーパーマリオブラザーズ",
            "ゼルダの伝説 時のオカリナ",
            "ポケットモンスター 赤・緑",
            "テトリス",
            "マインクラフト",
            "グランド・セフト・オートV",
            "ファイナルファンタジーVII",
            "ウィッチャー3 ワイルドハント",
            "フォートナイト",
            "リーグ・オブ・レジェンド",
            "コール オブ デューティ モダン・ウォーフェア",
            "オーバーウォッチ",
            "カウンターストライク グローバルオフェンシブ",
            "大乱闘スマッシュブラザーズDX",
            "ワールド オブ ウォークラフト",
            "マリオカート8 デラックス",
            "スカイリム",
            "あつまれ どうぶつの森",
            "フォールアウト4",
            "アモングアス",
            "ソニック・ザ・ヘッジホッグ",
            "ヘイロー: コンバット・エボルブド",
            "レッド・デッド・リデンプション2",
            "モータルコンバット",
            "スタークラフト",
            "ストリートファイターII",
            "ダークソウル",
            "ドゥーム",
            "ザ・シムズ",
            "FIFA",
            "バイオハザード",
            "ギアーズ・オブ・ウォー",
            "マスエフェクト",
            "ハーフライフ",
            "ディアブロII",
            "メタルギアソリッド",
            "キングダム ハーツ",
            "ベヨネッタ",
            "アサシン クリード",
            "悪魔城ドラキュラ",
            "クラッシュ・バンディクー",
            "バイオショック",
            "アンチャーテッド",
            "ゴッド・オブ・ウォー",
            "デッドスペース",
            "ボーダーランズ",
            "ファークライ",
            "デウスエクス",
            "ワンダと巨像",
        ],
        "movie": [
            "スター・ウォーズ エピソード4 新たなる希望",
            "ジュラシック・パーク",
            "ハリー・ポッターと賢者の石",
            "タイタニック",
            "アバター",
            "トイ・ストーリー",
            "インディ・ジョーンズ/レイダース・オブ・ロストアーク",
            "シンドラーのリスト",
            "ライオン・キング",
            "ゴッドファーザー",
            "ターミネーター2",
            "ハンガー・ゲーム",
            "アイアンマン",
            "フォレスト・ガンプ/一期一会",
            "パイレーツ・オブ・カリビアン",
            "マトリックス",
            "ロード・オブ・ザ・リング/王の帰還",
            "スパイダーマン",
            "ミッション:インポッシブル",
            "ジョーズ",
            "アントマン",
            "スタートレック",
            "バットマン ビギンズ",
            "ハンコック",
            "ゴーストバスターズ",
            "バック・トゥ・ザ・フューチャー",
            "エイリアン",
            "エクソシスト",
            "エターナル・サンシャイン",
            "グリーン・マイル",
            "バーフバリ",
            "マッドマックス 怒りのデス・ロード",
            "ロッキー",
            "ローマの休日",
            "ショーシャンクの空に",
            "ブラックパンサー",
            "ゴッドファーザー PART II",
            "ウォーターワールド",
            "グラディエーター",
            "ダークナイト",
            "シャイニング",
            "ガーディアンズ・オブ・ギャラクシー",
            "プレデター",
            "ハンガーゲーム2",
            "ハンターゲーム3",
            "ハリー・ポッターと死の秘宝",
            "スターウォーズ エピソード7 フォースの覚醒",
            "スターウォーズ エピソード8 最後のジェダイ",
            "スターウォーズ エピソード9 スカイウォーカーの夜明け",
            "バイオハザード",
            "ファイナル・デスティネーション",
            "アベンジャーズ",
            "アベンジャーズ: エンドゲーム",
            "アベンジャーズ: インフィニティ・ウォー",
            "アイアンマン2",
            "アイアンマン3",
            "シビル・ウォー/キャプテン・アメリカ",
            "アントマン&ワスプ",
            "バック・トゥ・ザ・フューチャー2",
            "バック・トゥ・ザ・フューチャー3",
            "マッドマックス2",
            "マッドマックス3",
            "ロード・オブ・ザ・リング/二つの塔",
            "ロード・オブ・ザ・リング/王の帰還",
            "トランスフォーマー",
            "トランスフォーマー2",
            "トランスフォーマー3",
            "トランスフォーマー4",
            "トランスフォーマー5",
            "トランスフォーマー6",
            "スパイダーマン2",
            "スパイダーマン3",
            "アメイジング・スパイダーマン",
            "アメイジング・スパイダーマン2",
            "ミッション:インポッシブル2",
            "ミッション:インポッシブル3",
            "ミッション:インポッシブル4",
            "ミッション:インポッシブル5",
            "ミッション:インポッシブル6",
            "ミッション:インポッシブル7",
            "ジョーズ2",
            "ジョーズ3",
            "ジョーズ4",
            "アリゲーター",
            "アリゲーター2",
            "アリゲーター3",
            "キングコング",
            "キングコング2",
            "キングコング3",
            "アナコンダ",
            "アナコンダ2",
            "アナコンダ3",
            "ジュラシックパーク2",
            "ジュラシックパーク3",
            "ジュラシックワールド",
            "ジュラシックワールド2",
            "ジュラシックワールド3",
            "パイレーツ・オブ・カリビアン2",
            "パイレーツ・オブ・カリビアン3",
            "パイレーツ・オブ・カリビアン4",
            "パイレーツ・オブ・カリビアン5",
        ],
        "sports": [
            "サッカー",
            "野球",
            "バスケットボール",
            "テニス",
            "ゴルフ",
            "アメリカンフットボール",
            "ラグビー",
            "ホッケー",
            "バレーボール",
            "クリケット",
            "ボクシング",
            "柔道",
            "相撲",
            "格闘技",
            "ウィンタースポーツ",
            "フィギュアスケート",
            "水泳",
            "陸上競技",
            "バドミントン",
            "卓球",
            "モータースポーツ",
            "自転車競技",
            "ボウリング",
            "ハンドボール",
            "カーリング",
            "スノーボード",
            "スキージャンプ",
            "アイスホッケー",
            "フットサル",
            "サーフィン",
            "スケートボード",
            "クロスカントリースキー",
            "アーチェリー",
            "ボート競技",
            "スカッシュ",
            "ボクシング",
            "レスリング",
            "トライアスロン",
            "ボディービルディング",
            "アメリカンフットボール",
            "ハンドボール",
            "フェンシング",
            "カヌー競技",
            "ローラースポーツ",
            "ハイキング",
            "スポーツクライミング",
            "アーティスティックスイミング",
            "馬術",
        ],
        "lifestyle": [
            "グルメ",
            "フード",
            "料理",
            "レシピ",
            "食材",
            "調理法",
            "味",
            "香り",
            "食感",
            "盛り付け",
            "料理人",
            "シェフ",
            "レストラン",
            "カフェ",
            "居酒屋",
            "バー",
            "食事",
            "朝食",
            "昼食",
            "夕食",
            "デザート",
            "コーヒー",
            "紅茶",
            "ワイン",
            "ビール",
            "日本酒",
            "スイーツ",
            "パン",
            "ピザ",
            "寿司",
            "刺身",
            "焼き魚",
            "肉料理",
            "魚料理",
            "野菜料理",
            "スープ",
            "麺料理",
            "カレー",
            "スパイス",
            "ハーブ",
            "ファッション",
            "服",
            "洋服",
            "和服",
            "アクセサリー",
            "バッグ",
            "靴",
            "ハイヒール",
            "スニーカー",
            "アウター",
            "ジャケット",
            "コート",
            "シャツ",
            "パンツ",
            "スカート",
        ],
        "science": [
            "化学反応",
            "原子",
            "元素",
            "分子",
            "イオン",
            "化合物",
            "化学式",
            "原子番号",
            "周期表",
            "化学結合",
            "イオン結合",
            "共有結合",
            "水素結合",
            "電子",
            "原子核",
            "質量数",
            "原子量",
            "モル",
            "融点",
            "沸点",
            "密度",
            "物質",
            "化学変化",
            "酸",
            "塩基",
            "中和反応",
            "酸化還元反応",
            "酸素",
            "水素",
            "窒素",
            "炭素",
            "鉄",
            "金",
            "銀",
            "銅",
            "アルミニウム",
            "水",
            "塩",
            "二酸化炭素",
            "酸素ガス",
            "窒素ガス",
            "水素ガス",
            "気体",
            "液体",
            "固体",
            "溶液",
            "分離技術",
            "ろ過",
            "蒸留",
            "濾過",
            "蒸発",
        ],
        "history_humanity": [
            "歴史",
            "時代",
            "年号",
            "戦国時代",
            "江戸時代",
            "明治維新",
            "第二次世界大戦",
            "戦争",
            "革命",
            "政治",
            "政治家",
            "皇帝",
            "王",
            "国王",
            "首相",
            "大統領",
            "帝国",
            "共和国",
            "帝国主義",
            "植民地",
            "革命",
            "独立",
            "統一",
            "分裂",
            "世界史",
            "日本史",
            "文学",
            "詩",
            "小説",
            "物語",
            "キャラクター",
            "登場人物",
            "設定",
            "プロット",
            "モチーフ",
            "テーマ",
            "作者",
            "読者",
            "視点",
            "語り手",
            "物語構造",
            "登場人物の性格",
            "対話",
            "言葉",
            "表現",
            "比喩",
            "象徴",
            "意味",
            "解釈",
            "文学史",
            "ことわざ",
            "諺",
            "慣用句",
        ],
        "prefectures": [
            "北海道",
            "青森県",
            "岩手県",
            "宮城県",
            "秋田県",
            "山形県",
            "福島県",
            "茨城県",
            "栃木県",
            "群馬県",
            "埼玉県",
            "千葉県",
            "東京都",
            "神奈川県",
            "新潟県",
            "富山県",
            "石川県",
            "福井県",
            "山梨県",
            "長野県",
            "岐阜県",
            "静岡県",
            "愛知県",
            "三重県",
            "滋賀県",
            "京都府",
            "大阪府",
            "兵庫県",
            "奈良県",
            "和歌山県",
            "鳥取県",
            "島根県",
            "岡山県",
            "広島県",
            "山口県",
            "徳島県",
            "香川県",
            "愛媛県",
            "高知県",
            "福岡県",
            "佐賀県",
            "長崎県",
            "熊本県",
            "大分県",
            "宮崎県",
            "鹿児島県",
            "沖縄県",
        ],
    }

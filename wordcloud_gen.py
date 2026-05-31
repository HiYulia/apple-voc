"""
词云生成模块，供 dashboard.py 调用
"""
import re
import io
import os
import jieba
import numpy as np
from PIL import Image
from wordcloud import WordCloud, STOPWORDS

# ── 停用词 ─────────────────────────────────────────────────────────
STOPWORDS_ZH = {
    # 虚词/助词
    "的", "了", "是", "我", "你", "他", "她", "它", "们", "这", "那", "有",
    "在", "和", "与", "或", "但", "就", "也", "都", "很", "非常", "真的",
    "一个", "一些", "这个", "那个", "可以", "因为", "所以", "如果", "虽然",
    "还是", "就是", "其实", "已经", "一直", "没有", "现在", "大家", "自己",
    "感觉", "觉得", "觉", "感", "时候", "什么", "怎么", "为什么",
    "不是", "不会", "不用", "不太", "不错", "不好", "比较", "应该",
    "一样", "这样", "那么", "这么", "如何", "能够", "需要", "可能",
    "之前", "之后", "以后", "以前", "今年", "去年", "出来", "进去",
    "知道", "发现", "还有", "没有", "不了", "不如", "很多", "以及",
    "特别", "大约", "除了", "时间", "有没有", "差不多", "而且", "然后",
    "虽然", "但是", "不过", "只是", "确实", "毕竟", "反正", "总之",
    "有点", "有些", "好像", "看看", "试试", "想想",
    # 动词泛词
    "用", "买", "换", "选", "做", "来", "去", "说", "看", "想",
    "买了", "用了", "换了", "感谢", "谢谢", "请问",
    "建议", "推荐", "觉得", "感觉",
    # 产品名泛词
    "手机", "苹果", "iPhone", "iphone",
    "17", "16", "15", "14", "13",
    "pro", "Pro", "max", "Max", "air", "Air", "系列", "版本",
    # 语气词
    "啊", "哦", "嗯", "吧", "呢", "哈", "嘛", "吗", "哇",
    "哎", "哟", "呀", "嘿", "哈哈", "哈哈哈",
    # 社交媒体
    "话题", "标签", "分享", "转发", "评论", "点赞", "收藏", "关注",
    "置顶", "回复", "楼主", "博主",
    # 数字/字母噪音
    "R", "r", "null", "None", "nan",
}
STOPWORDS_EN = STOPWORDS | {
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "have",
    "has", "had", "do", "does", "did", "will", "would", "could", "should",
    "it", "its", "this", "that", "these", "those", "i", "you", "he", "she",
    "we", "they", "my", "your", "his", "her", "our", "their", "phone",
    "iPhone", "apple", "Apple",
}

# 字体路径（优先 repo 内字体，再 fallback 系统字体）
_HERE = os.path.dirname(os.path.abspath(__file__))

FONT_CANDIDATES = [
    os.path.join(_HERE, "assets", "wqy-microhei.ttc"),     # repo 内置（优先）
    "/System/Library/Fonts/STHeiti Medium.ttc",            # macOS
    "/System/Library/Fonts/Hiragino Sans GB.ttc",          # macOS
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",     # Ubuntu/Debian
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]

def get_font_path():
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def tokenize(texts: list[str], lang: str = "zh") -> str:
    """分词并过滤停用词，返回空格分隔的词串"""
    combined = " ".join(str(t) for t in texts)
    # 清理 emoji、话题标签、HTML、特殊符号
    combined = re.sub(r"#\S+", "", combined)
    combined = re.sub(r"\[[\w]+R?\]", "", combined)
    combined = re.sub(r"<[^>]+>", "", combined)
    combined = re.sub(r"[^一-鿿㐀-䶿a-zA-Z0-9\s]", " ", combined)  # 只保留中英文数字

    if lang == "zh":
        words = jieba.cut(combined, cut_all=False)
        filtered = [
            w.strip() for w in words
            if len(w.strip()) >= 2
            and w.strip() not in STOPWORDS_ZH
            and not w.strip().isdigit()
            and not re.match(r'^[a-zA-Z0-9]{1,2}$', w.strip())
            and re.search(r'[一-鿿]', w)  # 必须包含至少一个中文字符
        ]
    else:
        words = re.findall(r'\b[a-zA-Z]{3,}\b', combined)
        filtered = [w.lower() for w in words if w.lower() not in STOPWORDS_EN]

    return " ".join(filtered)


def make_wordcloud(
    texts: list[str],
    lang: str = "zh",
    sentiment: str = "all",   # all | positive | negative
    width: int = 800,
    height: int = 380,
) -> Image.Image | None:
    """生成词云，返回 PIL Image"""
    if not texts:
        return None

    font_path = get_font_path()
    if font_path is None:
        return None

    word_str = tokenize(texts, lang)
    if not word_str.strip():
        return None

    # 配色方案
    color_schemes = {
        "all":      ["#6366f1", "#8b5cf6", "#a78bfa", "#c4b5fd", "#818cf8"],
        "positive": ["#10b981", "#34d399", "#6ee7b7", "#059669", "#047857"],
        "negative": ["#ef4444", "#f87171", "#fca5a5", "#dc2626", "#b91c1c"],
    }
    colors = color_schemes.get(sentiment, color_schemes["all"])

    def color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        return colors[random_state.randint(0, len(colors) - 1)]

    try:
        wc = WordCloud(
            font_path=font_path,
            width=width,
            height=height,
            background_color="#1e2235",
            max_words=50,           # 减少词数，更清晰
            min_font_size=14,       # 小字直接不显示
            max_font_size=100,      # 大词更突出
            prefer_horizontal=0.85,
            color_func=color_func,
            collocations=False,
            margin=6,               # 词间距加大
            relative_scaling=0.6,  # 词频差异更明显
        ).generate(word_str)
        return wc.to_image()
    except Exception as e:
        print(f"Wordcloud error: {e}")
        return None


def pil_to_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

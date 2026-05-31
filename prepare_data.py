"""
把下载的 iPhone 11 真实评论 + 少量生成的 iPhone 17 中文评论合并，
输出统一格式的 data/reviews_raw.csv
"""
import pandas as pd
import random

random.seed(42)

# ── 1. 加载真实英文评论 ────────────────────────────────────────────
raw = pd.read_csv("data/iphone11_raw.csv", index_col=0)
raw = raw.rename(columns={"Text": "content", "Rating": "score", "Time": "creation_time"})
raw["model"] = "iPhone 11"
raw["product_id"] = "en_amazon"
raw["user_level"] = "unknown"
raw["reply_count"] = 0
raw["useful_count"] = 0
en_df = raw[["model", "product_id", "content", "score", "creation_time", "user_level", "reply_count", "useful_count"]].copy()
en_df = en_df[en_df["content"].str.len() > 20].reset_index(drop=True)

# ── 2. 生成 iPhone 17 中文模拟评论（覆盖各维度）────────────────────
CN_TEMPLATES = {
    "battery": [
        ("续航比16强多了，一天下来还有30%电量，满分！", 5),
        ("电池不经用，刷了一天抖音晚上8点就没电了", 2),
        ("充电速度还是太慢，都2026年了还是20W", 3),
        ("ProMax续航真的够用，出差两天不带充电器没问题", 5),
        ("A18芯片确实省电，同样使用强度比前代多用2小时", 4),
    ],
    "screen": [
        ("ProMotion屏幕丝滑，打游戏爽到飞起", 5),
        ("户外亮度不错，阳光下也能看清", 4),
        ("屏幕比较容易沾指纹，擦起来麻烦", 3),
        ("2000nit峰值亮度，夏天户外使用没有任何问题", 5),
        ("折射率一般，和三星S系列比还是差点意思", 3),
    ],
    "camera": [
        ("拍猫超清晰，夜间模式也很强，非常满意", 5),
        ("前置摄像头美颜太过度，拍出来不像本人", 2),
        ("视频防抖太厉害了，骑自行车拍也很稳", 5),
        ("4800万像素但实际照片观感一般，不如华为", 3),
        ("夜景拍摄进步明显，路灯下的细节都能看清", 4),
    ],
    "performance": [
        ("A18 Pro跑分碾压安卓旗舰，不愧苹果", 5),
        ("发热问题明显，玩原神20分钟手机烫手", 2),
        ("日常使用流畅无卡顿，多任务切换很顺滑", 5),
        ("游戏帧率偶尔会降，不是很稳定", 3),
        ("速度飞快，和上代比没什么感觉，不值升级", 3),
    ],
    "design": [
        ("钛金属边框手感超好，比之前的不锈钢轻多了", 5),
        ("新增橙色太好看了，拿出来回头率很高", 5),
        ("机身太重，单手握持很累", 2),
        ("背板磨砂玻璃不错，防滑耐脏", 4),
        ("厚度比上代薄了一点，进步不大", 3),
    ],
    "price_value": [
        ("价格有点贵，但用起来确实值", 4),
        ("8499起步，普通人消费不起", 2),
        ("活动价打了九折，性价比还可以接受", 4),
        ("同价位买华为Mate更划算，苹果溢价太高", 2),
        ("用了5年苹果，每代都升级，忠实用户", 5),
    ],
    "software": [
        ("iOS 19系统流畅，但自定义程度太低了", 3),
        ("Apple Intelligence中文版终于来了，但功能还不完善", 3),
        ("系统更新后续航变差，等待优化", 2),
        ("和iPad、Mac的生态联动很方便，接力功能很好用", 5),
        ("App Store下架了很多app，找不到想用的软件", 2),
    ],
    "after_sales": [
        ("天才吧预约很方便，换屏速度快", 5),
        ("售后态度差，保修期内换电池还要收费", 1),
        ("AppleCare+买了很值，直接换了台新机", 5),
        ("找第三方维修被拒绝激活，很麻烦", 2),
        ("官方客服响应慢，等了3天才解决问题", 2),
    ],
}

MODELS = ["iPhone 17", "iPhone 17 Pro", "iPhone 17 Pro Max", "iPhone 17e"]
MODEL_IDS = {
    "iPhone 17": "100278222276",
    "iPhone 17 Pro": "100209267859",
    "iPhone 17 Pro Max": "100278222022",
    "iPhone 17e": "100328062610",
}
USER_LEVELS = ["钻石会员", "金牌会员", "普通会员", "银牌会员"]

cn_rows = []
for category, templates in CN_TEMPLATES.items():
    for _ in range(25):  # 每个类别生成25条，共200条
        content, base_score = random.choice(templates)
        model = random.choice(MODELS)
        score = min(5, max(1, base_score + random.randint(-1, 1)))
        cn_rows.append({
            "model": model,
            "product_id": MODEL_IDS[model],
            "content": content,
            "score": score,
            "creation_time": f"2026-0{random.randint(1,5)}-{random.randint(1,28):02d}",
            "user_level": random.choice(USER_LEVELS),
            "reply_count": random.randint(0, 20),
            "useful_count": random.randint(0, 50),
        })

cn_df = pd.DataFrame(cn_rows)

# ── 3. 合并保存 ───────────────────────────────────────────────────
combined = pd.concat([en_df, cn_df], ignore_index=True)
combined.to_csv("data/reviews_raw.csv", index=False, encoding="utf-8-sig")

print(f"英文真实评论: {len(en_df)}")
print(f"中文模拟评论: {len(cn_df)}")
print(f"总计: {len(combined)}")
print("\n前3条样本:")
print(combined[["model","content","score"]].head(3).to_string())

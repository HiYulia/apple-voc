import requests
import pandas as pd
import time
import random
import os

COOKIE = os.environ.get("JD_COOKIE", "")

PRODUCTS = {
    "iPhone 17":         {"sku": "100209267857", "shop": "1000000127", "category": "9987;653;655"},
    "iPhone 17 Pro":     {"sku": "100209268163", "shop": "1000000127", "category": "9987;653;655"},
    "iPhone 17 Pro Max": {"sku": "100276651725", "shop": "1000000127", "category": "9987;653;655"},
    "iPhone 17e":        {"sku": "100328062626", "shop": "1000000127", "category": "9987;653;655"},
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://item.jd.com/100209267857.html",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Cookie": COOKIE,
}


def fetch_page(sku: str, shop: str, page: int, score: int = 0) -> list[dict]:
    url = (
        f"https://club.jd.com/comment/skuProductPageComments.action"
        f"?productId={sku}&score={score}&sortType=5&page={page}&pageSize=10"
        f"&isShadowSku=0&fold=1&shieldCurrentComment=1&shopId={shop}"
    )
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
        return data.get("comments", [])
    except Exception as e:
        print(f"    页面 {page} 失败: {e}")
        return []


def scrape_model(model_name: str, info: dict, pages: int = 50) -> list[dict]:
    sku, shop = info["sku"], info["shop"]
    rows = []

    # 抓全部评论 + 单独抓差评（score=1,2 保证负面样本）
    for score, label in [(0, "全部"), (1, "差评1星"), (2, "差评2星")]:
        empty_count = 0
        max_pages = pages if score == 0 else 10
        for page in range(max_pages):
            comments = fetch_page(sku, shop, page, score=score)
            if not comments:
                empty_count += 1
                if empty_count >= 3:
                    break
                continue
            empty_count = 0
            for c in comments:
                rows.append({
                    "model":         model_name,
                    "sku":           sku,
                    "content":       c.get("content", "").strip(),
                    "score":         c.get("score", 0),
                    "creation_time": c.get("creationTime", ""),
                    "user_level":    c.get("userLevelName", ""),
                    "reply_count":   c.get("replyCount", 0),
                    "useful_count":  c.get("usefulVoteCount", 0),
                    "nickname":      c.get("nickname", ""),
                })
            print(f"  [{model_name}][{label}] page {page+1} — {len(comments)} 条，累计 {len(rows)} 条")
            time.sleep(random.uniform(1.0, 2.0))

    # 去重
    seen = set()
    unique = []
    for r in rows:
        key = (r["sku"], r["content"][:30], r["creation_time"])
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def scrape_all(pages_per_model: int = 50):
    os.makedirs("data", exist_ok=True)
    all_rows = []

    for model_name, info in PRODUCTS.items():
        print(f"\n开始抓取 {model_name} (sku={info['sku']})...")
        rows = scrape_model(model_name, info, pages=pages_per_model)
        all_rows.extend(rows)
        print(f"  → {model_name} 完成，共 {len(rows)} 条")

    df = pd.DataFrame(all_rows)
    df = df[df["content"].str.len() > 5].reset_index(drop=True)
    df.to_csv("data/reviews_raw.csv", index=False, encoding="utf-8-sig")
    print(f"\n✓ 共保存 {len(df)} 条评论到 data/reviews_raw.csv")
    return df


if __name__ == "__main__":
    if not COOKIE:
        print("请设置 JD_COOKIE 环境变量")
        exit(1)
    df = scrape_all(pages_per_model=50)
    print(df[["model", "content", "score"]].head(5).to_string())

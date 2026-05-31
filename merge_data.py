"""
合并新下载的评论数据到 reviews_raw.csv
用法: python merge_data.py <新文件路径>
"""
import sys
import pandas as pd

NEW_FILE = sys.argv[1] if len(sys.argv) > 1 else "~/Downloads/iphone17_reviews.csv"
RAW_CSV  = "data/reviews_raw.csv"

COLS = ["model", "sku", "content", "score", "creation_time", "user_level", "reply_count", "useful_count"]

def load_new(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df.rename(columns={"time": "creation_time", "level": "user_level"})
    for col in ["reply_count", "useful_count"]:
        if col not in df.columns:
            df[col] = 0
    if "nickname" not in df.columns:
        df["nickname"] = ""
    df = df[df["content"].astype(str).str.len() > 5]
    return df

def merge():
    import os, pathlib
    path = pathlib.Path(NEW_FILE).expanduser()
    if not path.exists():
        print(f"文件不存在: {path}")
        return

    new_df = load_new(str(path))
    print(f"新文件: {len(new_df)} 条")

    existing = pd.read_csv(RAW_CSV)
    print(f"现有数据: {len(existing)} 条")

    combined = pd.concat([existing, new_df], ignore_index=True)
    # 按内容去重
    combined = combined.drop_duplicates(subset=["content"], keep="first")
    combined.to_csv(RAW_CSV, index=False, encoding="utf-8-sig")
    print(f"✓ 合并后: {len(combined)} 条 → {RAW_CSV}")
    print("\n机型分布:")
    print(combined["model"].value_counts().to_string())
    print("\n评分分布:")
    print(combined["score"].value_counts().sort_index().to_string())

if __name__ == "__main__":
    merge()

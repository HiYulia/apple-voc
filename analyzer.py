import re
import json
import time
import pandas as pd
from openai import OpenAI

import os
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_KEY:
    raise EnvironmentError("Please set OPENROUTER_API_KEY environment variable")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
)

SYSTEM_PROMPT = """你是一个消费电子产品用户反馈分析专家，专门分析 iPhone 用户评论。

对每条评论，输出 JSON 对象，包含以下字段：
- category: 主要反馈类别（从下列选一个）
  battery       续航/电池/充电
  camera        拍照/摄像/画质
  screen        屏幕/显示/亮度
  performance   性能/流畅/发热/芯片
  design        外观/重量/颜色/做工
  price_value   价格/性价比/国补/分期
  software      系统/App/功能/iOS
  after_sales   售后/物流/维修/退换
  purchase_decision  选机/纠结/买哪款/值不值得买
  general_positive   正面但无具体维度（好用/满意/推荐）
  general_negative   负面但无具体维度（失望/后悔/不好用）
  off_topic          与 iPhone 产品体验无关

- sentiment: positive / negative / neutral

- key_point: 用10字以内中文概括核心观点，off_topic 填"无关"

只输出 JSON，不要其他文字。"""


def classify_batch(texts: list[str]) -> list[dict]:
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(texts))
    prompt = f"请分析以下{len(texts)}条评论，返回 JSON 数组，每条对应一个对象：\n\n{numbered}"

    resp = client.chat.completions.create(
        model="anthropic/claude-haiku-4-5",
        max_tokens=2000,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
    )
    text = resp.choices[0].message.content.strip()
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def analyze_all(input_csv="data/reviews_raw.csv", output_csv="data/reviews_analyzed.csv"):
    df = pd.read_csv(input_csv)
    print(f"载入 {len(df)} 条评论，开始 Claude 语义分类...\n")

    results = []
    batch_size = 15
    total_batches = (len(df) - 1) // batch_size + 1

    for i in range(0, len(df), batch_size):
        batch_texts = df["content"].iloc[i:i+batch_size].astype(str).tolist()
        batch_num = i // batch_size + 1
        try:
            analyzed = classify_batch(batch_texts)
            # 补齐长度防止API少返回
            while len(analyzed) < len(batch_texts):
                analyzed.append({"category": "off_topic", "sentiment": "neutral", "key_point": "解析失败"})
            results.extend(analyzed[:len(batch_texts)])
            print(f"  批次 {batch_num}/{total_batches} ✓  (+{len(batch_texts)}条，累计{len(results)}条)")
        except Exception as e:
            print(f"  批次 {batch_num} 失败: {e}，使用默认值")
            results.extend([{"category": "off_topic", "sentiment": "neutral", "key_point": "解析失败"}] * len(batch_texts))
        time.sleep(0.3)

    analyzed_df = pd.DataFrame(results)
    final = pd.concat([df.reset_index(drop=True), analyzed_df.reset_index(drop=True)], axis=1)

    # 去掉 off_topic
    before = len(final)
    final = final[final["category"] != "off_topic"].reset_index(drop=True)
    print(f"\n过滤 off_topic 后: {before} → {len(final)} 条")

    final.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"✓ 保存到 {output_csv}\n")

    print("类别分布:")
    print(final["category"].value_counts().to_string())
    print("\n情感分布:")
    print(final["sentiment"].value_counts().to_string())
    return final


if __name__ == "__main__":
    analyze_all()

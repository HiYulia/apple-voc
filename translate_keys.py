import os, json, re, time, pandas as pd
from openai import OpenAI

OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY", "")
if not OPENROUTER_KEY:
    raise EnvironmentError("Please set OPENROUTER_API_KEY environment variable")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_KEY,
)

df = pd.read_csv("data/reviews_analyzed.csv")
if "key_point_en" not in df.columns:
    df["key_point_en"] = ""

mask = df["key_point_en"].isna() | (df["key_point_en"] == "")
print(f"需要翻译: {mask.sum()} 条")

texts  = df.loc[mask, "key_point"].tolist()
indices = df.index[mask].tolist()

SYSTEM = "You are a translator. Translate each Chinese phrase to concise English (max 6 words). Return only a JSON array of strings, same order as input."

def translate_batch(batch):
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(batch))
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model="anthropic/claude-haiku-4-5",
                max_tokens=1000,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": numbered},
                ],
            )
            raw = resp.choices[0].message.content.strip()
            # strip code fences
            raw = re.sub(r"^```[a-z]*\n?", "", raw)
            raw = re.sub(r"\n?```$", "", raw)
            return json.loads(raw)
        except Exception as e:
            print(f"    retry {attempt+1}: {e}")
            time.sleep(1)
    return [t for t in batch]  # fallback: keep original

results = []
batch_size = 30
total = (len(texts) - 1) // batch_size + 1
for i in range(0, len(texts), batch_size):
    batch = texts[i:i+batch_size]
    translated = translate_batch(batch)
    while len(translated) < len(batch):
        translated.append(batch[len(translated)])
    results.extend(translated[:len(batch)])
    print(f"  批次 {i//batch_size+1}/{total} ✓  ({len(results)}/{len(texts)})")
    time.sleep(0.3)

for idx, en in zip(indices, results):
    df.at[idx, "key_point_en"] = en

df.to_csv("data/reviews_analyzed.csv", index=False, encoding="utf-8-sig")
print("\n✓ 翻译完成")
print(df[["key_point", "key_point_en"]].head(8).to_string())

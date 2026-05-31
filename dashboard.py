import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from i18n import t, cat_label, src_label

# ── Page config ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Apple VOC Dashboard",
    layout="wide",
    page_icon="📱",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.stApp { background: #0f1117; }
[data-testid="stSidebar"] {
    background: #1a1d27;
    border-right: 1px solid #2d3147;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

.metric-card {
    background: linear-gradient(135deg, #1e2235 0%, #252a3d 100%);
    border: 1px solid #2d3147;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: transform 0.2s;
    height: 100%;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.2;
}
.metric-label {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.section-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #6366f1;
    display: inline-block;
}

.badge {
    display: inline-block;
    background: #1e2235;
    border: 1px solid #2d3147;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.75rem;
    color: #94a3b8;
    margin-right: 8px;
    margin-bottom: 6px;
}

.insight-card {
    background: #1e2235;
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid;
    height: 100%;
}
.insight-green  { border-left-color: #10b981; }
.insight-red    { border-left-color: #ef4444; }
.insight-blue   { border-left-color: #6366f1; }
.insight-label  { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.insight-value  { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; margin-top: 4px; }

.quote-card {
    background: #1e2235;
    border: 1px solid #2d3147;
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 10px;
    position: relative;
}
.quote-text {
    color: #cbd5e1;
    font-size: 0.88rem;
    line-height: 1.6;
    margin-bottom: 8px;
}
.quote-meta {
    font-size: 0.72rem;
    color: #64748b;
}
.quote-category {
    display: inline-block;
    background: #312e81;
    color: #a5b4fc;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.7rem;
    margin-right: 8px;
}
.quote-sentiment-pos { color: #10b981; }
.quote-sentiment-neg { color: #ef4444; }
.quote-sentiment-neu { color: #6366f1; }

hr { border-color: #2d3147 !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_THEME = dict(
    paper_bgcolor="#1e2235",
    plot_bgcolor="#1e2235",
    font=dict(family="Inter", color="#e2e8f0", size=12),
    margin=dict(l=12, r=12, t=36, b=12),
)
SENT_COLOR = {
    "positive": "#10b981",
    "negative": "#ef4444",
    "neutral":  "#6366f1",
    "mixed":    "#f59e0b",
}

# ── Language toggle ────────────────────────────────────────────────
st.sidebar.markdown("### 🌐 Language / 语言")
lang = st.sidebar.radio("", ["中文", "English"], label_visibility="collapsed")
L = "zh" if lang == "中文" else "en"

# ── Load data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    for path in ["data/reviews_analyzed.csv", "data/sample_reviews.csv"]:
        if os.path.exists(path):
            return pd.read_csv(path), path
    return None, None

df, data_path = load_data()
if df is None:
    st.error("No data found. Run analyzer.py to generate data.")
    st.stop()

is_sample = "sample" in data_path
if is_sample:
    st.sidebar.info("📊 " + ("展示样本数据（100条），运行 analyzer.py 获取完整数据" if L=="zh"
                             else "Showing sample data (100 reviews). Run analyzer.py for full insights."))

df["cat_label"]  = df["category"].apply(lambda x: cat_label(x, L))
df["src_label"]  = df["sku"].astype(str).apply(lambda x: src_label(x, L))
df["useful_count"] = pd.to_numeric(df["useful_count"], errors="coerce").fillna(0)
df["creation_time"] = pd.to_datetime(df["creation_time"], errors="coerce")
df["month"] = df["creation_time"].dt.to_period("M").astype(str)

# ── Sidebar filters ────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.markdown(f"### {t('filter_header', L)}")

products = [t("all", L)] + sorted(df["model"].dropna().unique().tolist())
sel_product = st.sidebar.selectbox(t("filter_product", L), products)

sources = [t("all", L)] + sorted(df["src_label"].unique().tolist())
sel_source = st.sidebar.selectbox(t("filter_source", L), sources)

sentiments = sorted(df["sentiment"].dropna().unique().tolist())
sel_sent = st.sidebar.multiselect(t("filter_sentiment", L), sentiments, default=sentiments)

fdf = df.copy()
if sel_product != t("all", L):  fdf = fdf[fdf["model"] == sel_product]
if sel_source  != t("all", L):  fdf = fdf[fdf["src_label"] == sel_source]
if sel_sent:                     fdf = fdf[fdf["sentiment"].isin(sel_sent)]

# ── Header ─────────────────────────────────────────────────────────
st.markdown(f"## 📱 {t('title', L)}")
st.markdown(f"<span style='color:#94a3b8;font-size:0.9rem'>{t('subtitle', L)}</span>",
            unsafe_allow_html=True)

time_min = df["creation_time"].dropna().min().strftime("%Y-%m-%d")
time_max = df["creation_time"].dropna().max().strftime("%Y-%m-%d")
src_counts = df["src_label"].value_counts()
badges = f'<span class="badge">📅 {time_min} → {time_max}</span>'
for k, v in src_counts.items():
    icon = "🟡" if ("小红书" in k or "XHS" in k) else "🔴"
    badges += f'<span class="badge">{icon} {k} {v:,}</span>'
st.markdown(f"<div style='margin:8px 0 20px'>{badges}</div>", unsafe_allow_html=True)

# ── Metrics ────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
for col, val, label in [
    (m1, f"{len(fdf):,}",                               t("total_reviews", L)),
    (m2, f"{(fdf['sentiment']=='positive').mean():.0%}", t("positive_rate", L)),
    (m3, f"{(fdf['sentiment']=='negative').mean():.0%}", t("negative_rate", L)),
    (m4, f"{(fdf['sentiment']=='neutral').mean():.0%}",  t("neutral_rate", L)),
    (m5, f"{fdf['category'].nunique()}",                 "反馈维度" if L=="zh" else "Dimensions"),
]:
    col.markdown(
        f'<div class="metric-card"><div class="metric-value">{val}</div>'
        f'<div class="metric-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════
# ROW 1: Top concerns + Sentiment distribution
# ══════════════════════════════════════════════════════════════════
r1l, r1r = st.columns(2)

with r1l:
    st.markdown(f'<div class="section-title">{t("top_concerns", L)}</div>', unsafe_allow_html=True)
    cat_counts = fdf["cat_label"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    fig1 = px.bar(
        cat_counts, x="count", y="category", orientation="h",
        color="count", color_continuous_scale=["#312e81", "#6366f1", "#a5b4fc"],
        labels={"count": t("count", L), "category": ""},
    )
    fig1.update_traces(marker_line_width=0)
    fig1.update_layout(**PLOTLY_THEME, height=340,
                       coloraxis_showscale=False,
                       yaxis=dict(categoryorder="total ascending", gridcolor="#2d3147"),
                       xaxis=dict(gridcolor="#2d3147"))
    st.plotly_chart(fig1, use_container_width=True)

with r1r:
    st.markdown(f'<div class="section-title">{t("sentiment_dist", L)}</div>', unsafe_allow_html=True)
    if fdf["model"].nunique() > 1 and sel_product == t("all", L):
        sent_df = fdf.groupby(["model", "sentiment"]).size().reset_index(name="count")
        fig2 = px.bar(sent_df, x="model", y="count", color="sentiment",
                      barmode="group", color_discrete_map=SENT_COLOR,
                      labels={"count": t("count", L), "model": "", "sentiment": t("sentiment", L)})
        fig2.update_layout(**PLOTLY_THEME, height=340,
                           xaxis=dict(gridcolor="#2d3147"),
                           yaxis=dict(gridcolor="#2d3147"),
                           legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
    else:
        sent_counts = fdf["sentiment"].value_counts().reset_index()
        fig2 = go.Figure(go.Pie(
            labels=sent_counts["sentiment"], values=sent_counts["count"],
            hole=0.55,
            marker_colors=[SENT_COLOR.get(s, "#94a3b8") for s in sent_counts["sentiment"]],
            textinfo="label+percent", textfont_size=12,
        ))
        fig2.update_layout(**PLOTLY_THEME, height=340,
                           legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════════════════════════
# ROW 2: Pos/Neg category comparison + Trend over time
# ══════════════════════════════════════════════════════════════════
r2l, r2r = st.columns(2)

with r2l:
    # ── FIX 1&2: Pos vs Neg per category, clearly separated ──────
    title_posneg = "各维度正负面分布" if L=="zh" else "Positive vs Negative by Category"
    st.markdown(f'<div class="section-title">{title_posneg}</div>', unsafe_allow_html=True)

    pos_by_cat = (fdf[fdf["sentiment"]=="positive"]
                  .groupby("cat_label").size().reset_index(name="count"))
    pos_by_cat["type"] = "positive"
    neg_by_cat = (fdf[fdf["sentiment"]=="negative"]
                  .groupby("cat_label").size().reset_index(name="count"))
    neg_by_cat["type"] = "negative"
    # Negative counts shown as positive bars (direction conveyed by color)
    combined = pd.concat([pos_by_cat, neg_by_cat])

    fig3 = px.bar(
        combined, x="count", y="cat_label", color="type",
        orientation="h", barmode="group",
        color_discrete_map={"positive": "#10b981", "negative": "#ef4444"},
        labels={"count": t("count", L), "cat_label": "", "type": t("sentiment", L)},
    )
    fig3.update_layout(**PLOTLY_THEME, height=340,
                       yaxis=dict(categoryorder="total ascending", gridcolor="#2d3147"),
                       xaxis=dict(gridcolor="#2d3147"),
                       legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
    st.plotly_chart(fig3, use_container_width=True)

with r2r:
    # ── FIX 3: Trend over time ────────────────────────────────────
    title_trend = "评论数量趋势（按月）" if L=="zh" else "Review Volume Trend (Monthly)"
    st.markdown(f'<div class="section-title">{title_trend}</div>', unsafe_allow_html=True)

    trend = (fdf.groupby(["month", "sentiment"]).size()
             .reset_index(name="count")
             .sort_values("month"))
    trend = trend[trend["month"].str.startswith(("2025","2026"))]

    if len(trend) > 0:
        fig4 = px.line(
            trend, x="month", y="count", color="sentiment",
            color_discrete_map=SENT_COLOR,
            markers=True,
            labels={"count": t("count", L), "month": "", "sentiment": t("sentiment", L)},
        )
        fig4.update_traces(line_width=2, marker_size=6)
        fig4.update_layout(**PLOTLY_THEME, height=340,
                           xaxis=dict(gridcolor="#2d3147", tickangle=-30),
                           yaxis=dict(gridcolor="#2d3147"),
                           legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Not enough time data" if L=="en" else "时间数据不足")

# ══════════════════════════════════════════════════════════════════
# ROW 3: Key Insights (FIXED)
# ══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown(f'<div class="section-title">🔍 {t("key_insights", L)}</div>',
            unsafe_allow_html=True)

# FIX 2: separate positive/negative category analysis
pos_df = fdf[fdf["sentiment"] == "positive"]
neg_df = fdf[fdf["sentiment"] == "negative"]
top_pos_cat = pos_df["cat_label"].value_counts().idxmax() if len(pos_df) else "-"
top_neg_cat = neg_df["cat_label"].value_counts().idxmax() if len(neg_df) else "-"
top_pos_n   = pos_df["cat_label"].value_counts().max() if len(pos_df) else 0
top_neg_n   = neg_df["cat_label"].value_counts().max() if len(neg_df) else 0
pos_rate    = (fdf["sentiment"] == "positive").mean()

most_disc = fdf["cat_label"].value_counts().idxmax() if len(fdf) else "-"

ins1, ins2, ins3, ins4 = st.columns(4)
for col, css, label_key, val in [
    (ins1, "insight-green", t("top_positive", L),   f"✅ {top_pos_cat} ({top_pos_n})"),
    (ins2, "insight-red",   t("top_negative", L),   f"⚠️ {top_neg_cat} ({top_neg_n})"),
    (ins3, "insight-blue",  t("positive_rate_label", L), f"📊 {pos_rate:.0%}"),
    (ins4, "insight-blue",  "最多讨论" if L=="zh" else "Most Discussed", f"💬 {most_disc}"),
]:
    col.markdown(
        f'<div class="insight-card {css}">'
        f'<div class="insight-label">{label_key}</div>'
        f'<div class="insight-value">{val}</div></div>',
        unsafe_allow_html=True,
    )

# ══════════════════════════════════════════════════════════════════
# ROW 4: FIX 4 — Representative quotes per category
# ══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
title_quotes = "代表性评论" if L=="zh" else "Representative Reviews"
st.markdown(f'<div class="section-title">💬 {title_quotes}</div>', unsafe_allow_html=True)

sub1, sub2 = ("最高赞正面评论", "最高赞负面评论") if L=="zh" else ("Top Positive Reviews", "Top Negative Reviews")

q_col1, q_col2 = st.columns(2)

def render_quotes(container, df_subset, max_quotes=4):
    top = (df_subset
           .sort_values("useful_count", ascending=False)
           .drop_duplicates(subset=["content"])
           .head(max_quotes))
    for _, row in top.iterrows():
        text = str(row["content"])[:160] + ("…" if len(str(row["content"])) > 160 else "")
        cat  = row.get("cat_label", "")
        sent = row.get("sentiment", "")
        likes = int(row.get("useful_count", 0))
        src  = row.get("src_label", "")
        sent_css = {"positive":"quote-sentiment-pos","negative":"quote-sentiment-neg"}.get(sent,"quote-sentiment-neu")
        sent_icon = {"positive":"👍","negative":"👎","neutral":"💬","mixed":"🔀"}.get(sent,"💬")
        container.markdown(
            f'<div class="quote-card">'
            f'<div class="quote-text">"{text}"</div>'
            f'<div class="quote-meta">'
            f'<span class="quote-category">{cat}</span>'
            f'<span class="{sent_css}">{sent_icon} {sent}</span>'
            f'  ·  ❤️ {likes}  ·  {src}'
            f'</div></div>',
            unsafe_allow_html=True,
        )

with q_col1:
    st.markdown(f"**{sub1}**")
    render_quotes(st, fdf[fdf["sentiment"]=="positive"], max_quotes=4)

with q_col2:
    st.markdown(f"**{sub2}**")
    render_quotes(st, fdf[fdf["sentiment"]=="negative"], max_quotes=4)

# ══════════════════════════════════════════════════════════════════
# Raw data expander
# ══════════════════════════════════════════════════════════════════
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
with st.expander(f"🗂 {t('raw_data', L)}", expanded=False):
    key_col = "key_point_en" if (L=="en" and "key_point_en" in fdf.columns) else "key_point"
    avail = ["model","content","score","cat_label","sentiment", key_col,"src_label","creation_time"]
    show  = [c for c in avail if c in fdf.columns]
    st.dataframe(
        fdf[show].rename(columns={
            "cat_label": t("category", L),
            "src_label": "Source/来源",
            "sentiment": t("sentiment", L),
        }),
        use_container_width=True, height=380,
    )
    st.download_button(
        f"⬇️ {t('download', L)}",
        fdf.to_csv(index=False, encoding="utf-8-sig"),
        "apple_voc.csv", "text/csv",
    )

# Footer
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#475569;font-size:0.78rem'>"
    "Built by <a href='https://medium.com/@yulianiu' style='color:#6366f1'>Yuyu</a> · "
    "<a href='https://github.com/HiYulia/apple-voc' style='color:#6366f1'>GitHub</a> · "
    "Data for research purposes only"
    "</div>",
    unsafe_allow_html=True,
)

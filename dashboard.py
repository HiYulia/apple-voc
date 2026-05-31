import pandas as pd
import streamlit as st
import plotly.express as px
from i18n import t, cat_label, src_label

st.set_page_config(
    page_title="Apple VOC Dashboard",
    layout="wide",
    page_icon="📱",
)

# ── Language toggle ────────────────────────────────────────────────
lang = st.sidebar.radio("🌐 Language / 语言", ["中文", "English"])
L = "zh" if lang == "中文" else "en"

# ── Load data ──────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return pd.read_csv("data/reviews_analyzed.csv")

try:
    df = load_data()
except FileNotFoundError:
    st.error("Run analyzer.py first to generate data.")
    st.stop()

# ── Derived labels ─────────────────────────────────────────────────
df["cat_label"] = df["category"].apply(lambda x: cat_label(x, L))
df["src_label"] = df["sku"].astype(str).apply(lambda x: src_label(x, L))

SENT_COLOR = {"positive": "#2ecc71", "negative": "#e74c3c",
              "neutral": "#95a5a6", "mixed": "#f39c12"}

# ── Sidebar filters ────────────────────────────────────────────────
st.sidebar.header(t("filter_header", L))

products = [t("all", L)] + sorted(df["model"].dropna().unique().tolist())
sel_product = st.sidebar.selectbox(t("filter_product", L), products)

sources = [t("all", L)] + sorted(df["src_label"].unique().tolist())
sel_source = st.sidebar.selectbox(t("filter_source", L), sources)

sentiments = sorted(df["sentiment"].unique().tolist())
sel_sent = st.sidebar.multiselect(t("filter_sentiment", L), sentiments, default=sentiments)

# ── Apply filters ──────────────────────────────────────────────────
fdf = df.copy()
if sel_product != t("all", L):
    fdf = fdf[fdf["model"] == sel_product]
if sel_source != t("all", L):
    fdf = fdf[fdf["src_label"] == sel_source]
if sel_sent:
    fdf = fdf[fdf["sentiment"].isin(sel_sent)]

# ── Header ─────────────────────────────────────────────────────────
st.title(f"📱 {t('title', L)}")
st.caption(t("subtitle", L))

# ── Data info bar ──────────────────────────────────────────────────
time_min = df["creation_time"].dropna().astype(str).min()[:10]
time_max = df["creation_time"].dropna().astype(str).max()[:10]
src_counts = df["src_label"].value_counts()
src_str = "  |  ".join(f"{k}: {v:,}" for k, v in src_counts.items())

with st.expander(f"ℹ️ {t('data_info', L)}", expanded=False):
    ic1, ic2 = st.columns(2)
    ic1.markdown(f"**{'时间范围' if L=='zh' else 'Date Range'}:** {time_min} → {time_max}")
    ic2.markdown(f"**{t('source_label', L)}:** {src_str}")
    st.markdown(
        "**数据说明 / Data Note:** " + (
            "数据来自小红书笔记与评论、B站视频评论，覆盖 iPhone 17 系列发布前后真实用户讨论。使用 Claude claude-haiku-4-5 进行语义分类。"
            if L == "zh" else
            "Data collected from Xiaohongshu (notes & comments) and Bilibili (video comments), covering real user discussions around the iPhone 17 launch. Classified using Claude claude-haiku-4-5 semantic analysis."
        )
    )

st.divider()

# ── Top metrics ────────────────────────────────────────────────────
st.subheader(t("overview", L))
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric(t("total_reviews", L), f"{len(fdf):,}")
c2.metric(t("positive_rate", L), f"{(fdf['sentiment']=='positive').mean():.1%}")
c3.metric(t("negative_rate", L), f"{(fdf['sentiment']=='negative').mean():.1%}")
c4.metric(t("neutral_rate", L),  f"{(fdf['sentiment']=='neutral').mean():.1%}")
c5.metric(t("date_range", L), f"{time_min[:7]} → {time_max[:7]}")

st.divider()

# ── Row 1 ──────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader(t("top_concerns", L))
    cat_counts = fdf["cat_label"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    fig = px.bar(cat_counts, x="count", y="category", orientation="h",
                 color="count", color_continuous_scale="Blues",
                 labels={"count": t("count", L), "category": t("category", L)})
    fig.update_layout(showlegend=False, coloraxis_showscale=False, height=340)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader(t("sentiment_dist", L))
    if sel_product == t("all", L):
        sent_model = fdf.groupby(["model", "sentiment"]).size().reset_index(name="count")
        fig2 = px.bar(sent_model, x="model", y="count", color="sentiment",
                      barmode="group", color_discrete_map=SENT_COLOR,
                      labels={"count": t("count", L), "model": t("filter_product", L),
                              "sentiment": t("sentiment", L)})
    else:
        sent_counts = fdf["sentiment"].value_counts().reset_index()
        fig2 = px.pie(sent_counts, names="sentiment", values="count",
                      color="sentiment", color_discrete_map=SENT_COLOR)
    fig2.update_layout(height=340)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2 ──────────────────────────────────────────────────────────
col3, col4 = st.columns(2)

with col3:
    st.subheader(t("category_pie", L))
    fig3 = px.pie(
        fdf["cat_label"].value_counts().reset_index().rename(columns={"cat_label":"label","count":"count"}),
        names="label", values="count", hole=0.4,
    )
    fig3.update_layout(height=320)
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader(t("neg_issues", L))
    neg_df = fdf[fdf["sentiment"] == "negative"]
    if len(neg_df) > 0:
        key_col = "key_point" if "key_point" in neg_df.columns else "key_issue"
        neg_issues = (neg_df.groupby(["cat_label", key_col])
                      .size().reset_index(name="count")
                      .sort_values("count", ascending=False).head(10))
        fig4 = px.bar(neg_issues, x="count", y=key_col, orientation="h",
                      color="cat_label",
                      labels={"count": t("count", L), key_col: t("issue", L),
                              "cat_label": t("category", L)})
        fig4.update_layout(height=320)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info(t("no_neg", L))

# ── Key Insights ───────────────────────────────────────────────────
st.divider()
st.subheader(f"🔍 {t('key_insights', L)}")
pos_cats = fdf[fdf["sentiment"] == "positive"]["cat_label"].value_counts()
neg_cats = fdf[fdf["sentiment"] == "negative"]["cat_label"].value_counts()
top_pos = pos_cats.idxmax() if len(pos_cats) else "-"
top_neg = neg_cats.idxmax() if len(neg_cats) else "-"

i1, i2, i3 = st.columns(3)
i1.success(f"**{t('top_positive', L)}**\n\n{top_pos}")
i2.error(f"**{t('top_negative', L)}**\n\n{top_neg}")
i3.info(f"**{t('positive_rate_label', L)}**\n\n{(fdf['sentiment']=='positive').mean():.1%}")

# ── Raw data ───────────────────────────────────────────────────────
with st.expander(t("raw_data", L)):
    avail = ["model", "content", "score", "cat_label", "sentiment",
             "key_point", "key_issue", "src_label", "creation_time"]
    show = [c for c in avail if c in fdf.columns]
    st.dataframe(fdf[show], use_container_width=True, height=400)
    st.download_button(
        t("download", L),
        fdf.to_csv(index=False, encoding="utf-8-sig"),
        "apple_voc_filtered.csv",
        "text/csv",
    )

import os
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
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
/* Font & base */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* Hide default Streamlit menu/footer */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
header    { visibility: hidden; }

/* Main background */
.stApp { background: #0f1117; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #1a1d27;
    border-right: 1px solid #2d3147;
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1e2235 0%, #252a3d 100%);
    border: 1px solid #2d3147;
    border-radius: 12px;
    padding: 20px 24px;
    text-align: center;
    transition: transform 0.2s;
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

/* Section headers */
.section-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e2e8f0;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #6366f1;
    display: inline-block;
}

/* Data info badge */
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

/* Insight cards */
.insight-card {
    background: #1e2235;
    border-radius: 12px;
    padding: 16px 20px;
    border-left: 4px solid;
    margin-bottom: 8px;
}
.insight-green  { border-left-color: #10b981; }
.insight-red    { border-left-color: #ef4444; }
.insight-blue   { border-left-color: #6366f1; }
.insight-label  { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.insight-value  { font-size: 1.15rem; font-weight: 600; color: #e2e8f0; margin-top: 4px; }

/* Chart containers */
.chart-container {
    background: #1e2235;
    border: 1px solid #2d3147;
    border-radius: 12px;
    padding: 4px;
}

/* Divider */
hr { border-color: #2d3147 !important; }

/* Scrollable table */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
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
    # Try full data first, fall back to sample
    for path in ["data/reviews_analyzed.csv", "data/sample_reviews.csv"]:
        if os.path.exists(path):
            df = pd.read_csv(path)
            return df, path
    return None, None

df, data_path = load_data()
if df is None:
    st.error("No data found. Run analyzer.py to generate data.")
    st.stop()

is_sample = "sample" in data_path
if is_sample:
    st.sidebar.info("📊 Showing sample data (100 reviews). Run analyzer.py with full data for complete insights.")

df["cat_label"] = df["category"].apply(lambda x: cat_label(x, L))
df["src_label"]  = df["sku"].astype(str).apply(lambda x: src_label(x, L))

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
if sel_product != t("all", L):   fdf = fdf[fdf["model"] == sel_product]
if sel_source  != t("all", L):   fdf = fdf[fdf["src_label"] == sel_source]
if sel_sent:                      fdf = fdf[fdf["sentiment"].isin(sel_sent)]

# ── Header ─────────────────────────────────────────────────────────
col_title, col_badge = st.columns([3, 1])
with col_title:
    st.markdown(f"## 📱 {t('title', L)}")
    st.markdown(f"<span style='color:#94a3b8;font-size:0.9rem'>{t('subtitle', L)}</span>",
                unsafe_allow_html=True)

time_min = df["creation_time"].dropna().astype(str).min()[:10]
time_max = df["creation_time"].dropna().astype(str).max()[:10]
src_counts = df["src_label"].value_counts()

badges_html = "".join(f'<span class="badge">📅 {time_min} → {time_max}</span>')
for k, v in src_counts.items():
    badges_html += f'<span class="badge">{'🟡' if '小红书' in k or 'XHS' in k else '🔴'} {k} {v:,}</span>'

st.markdown(f"<div style='margin: 8px 0 16px'>{badges_html}</div>", unsafe_allow_html=True)

# ── Top metrics ────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
metrics = [
    (f"{len(fdf):,}",                            t("total_reviews", L)),
    (f"{(fdf['sentiment']=='positive').mean():.0%}", t("positive_rate", L)),
    (f"{(fdf['sentiment']=='negative').mean():.0%}", t("negative_rate", L)),
    (f"{(fdf['sentiment']=='neutral').mean():.0%}",  t("neutral_rate", L)),
    (f"{fdf['category'].nunique()}",              "Categories" if L=="en" else "反馈维度"),
]
for col, (val, label) in zip([m1,m2,m3,m4,m5], metrics):
    col.markdown(
        f'<div class="metric-card"><div class="metric-value">{val}</div>'
        f'<div class="metric-label">{label}</div></div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)

# ── Row 1: concerns + sentiment ────────────────────────────────────
row1_l, row1_r = st.columns([1, 1])

with row1_l:
    st.markdown(f'<div class="section-title">{t("top_concerns", L)}</div>', unsafe_allow_html=True)
    cat_counts = fdf["cat_label"].value_counts().reset_index()
    cat_counts.columns = ["category", "count"]
    fig1 = px.bar(
        cat_counts, x="count", y="category", orientation="h",
        color="count", color_continuous_scale=["#312e81","#6366f1","#a5b4fc"],
        labels={"count": t("count", L), "category": ""},
    )
    fig1.update_traces(marker_line_width=0)
    fig1.update_layout(**PLOTLY_THEME, height=340, coloraxis_showscale=False,
                       yaxis=dict(categoryorder="total ascending", gridcolor="#2d3147"),
                       xaxis=dict(gridcolor="#2d3147"))
    st.plotly_chart(fig1, use_container_width=True)

with row1_r:
    st.markdown(f'<div class="section-title">{t("sentiment_dist", L)}</div>', unsafe_allow_html=True)
    if sel_product == t("all", L) and fdf["model"].nunique() > 1:
        sent_df = fdf.groupby(["model","sentiment"]).size().reset_index(name="count")
        fig2 = px.bar(
            sent_df, x="model", y="count", color="sentiment",
            barmode="group", color_discrete_map=SENT_COLOR,
            labels={"count": t("count", L), "model": "", "sentiment": t("sentiment", L)},
        )
        fig2.update_layout(**PLOTLY_THEME, height=340,
                           xaxis=dict(gridcolor="#2d3147"),
                           yaxis=dict(gridcolor="#2d3147"),
                           legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
    else:
        sent_counts = fdf["sentiment"].value_counts().reset_index()
        fig2 = go.Figure(go.Pie(
            labels=sent_counts["sentiment"], values=sent_counts["count"],
            hole=0.55,
            marker_colors=[SENT_COLOR.get(s,"#94a3b8") for s in sent_counts["sentiment"]],
            textinfo="label+percent",
            textfont_size=12,
        ))
        fig2.update_layout(**PLOTLY_THEME, height=340,
                           showlegend=True,
                           legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: neg issues + category donut ────────────────────────────
row2_l, row2_r = st.columns([1.2, 0.8])

with row2_l:
    st.markdown(f'<div class="section-title">{t("neg_issues", L)}</div>', unsafe_allow_html=True)
    neg_df = fdf[fdf["sentiment"] == "negative"]
    if len(neg_df) > 0:
        key_col = "key_point" if "key_point" in neg_df.columns else "key_issue"
        ni = (neg_df.groupby(["cat_label", key_col]).size()
              .reset_index(name="count").sort_values("count", ascending=True).tail(10))
        fig3 = px.bar(
            ni, x="count", y=key_col, orientation="h", color="cat_label",
            color_discrete_sequence=px.colors.qualitative.Set3,
            labels={"count": t("count", L), key_col: "", "cat_label": t("category", L)},
        )
        fig3.update_layout(**PLOTLY_THEME, height=340,
                           xaxis=dict(gridcolor="#2d3147"),
                           legend=dict(bgcolor="#1e2235", bordercolor="#2d3147"))
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info(t("no_neg", L))

with row2_r:
    st.markdown(f'<div class="section-title">{t("category_pie", L)}</div>', unsafe_allow_html=True)
    pie_df = fdf["cat_label"].value_counts().reset_index()
    pie_df.columns = ["label","count"]
    fig4 = go.Figure(go.Pie(
        labels=pie_df["label"], values=pie_df["count"],
        hole=0.5,
        textinfo="percent",
        textfont_size=11,
        marker=dict(line=dict(color="#0f1117", width=2)),
    ))
    fig4.update_layout(**PLOTLY_THEME, height=340,
                       showlegend=True,
                       legend=dict(bgcolor="#1e2235", bordercolor="#2d3147",
                                   font=dict(size=11)))
    st.plotly_chart(fig4, use_container_width=True)

# ── Key Insights ───────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
st.markdown(f'<div class="section-title">🔍 {t("key_insights", L)}</div>', unsafe_allow_html=True)

pos_cats = fdf[fdf["sentiment"]=="positive"]["cat_label"].value_counts()
neg_cats = fdf[fdf["sentiment"]=="negative"]["cat_label"].value_counts()
top_pos  = pos_cats.idxmax() if len(pos_cats) else "-"
top_neg  = neg_cats.idxmax() if len(neg_cats) else "-"
pos_rate = (fdf["sentiment"]=="positive").mean()

ins1, ins2, ins3 = st.columns(3)
ins1.markdown(
    f'<div class="insight-card insight-green">'
    f'<div class="insight-label">{t("top_positive", L)}</div>'
    f'<div class="insight-value">✅ {top_pos}</div></div>',
    unsafe_allow_html=True,
)
ins2.markdown(
    f'<div class="insight-card insight-red">'
    f'<div class="insight-label">{t("top_negative", L)}</div>'
    f'<div class="insight-value">⚠️ {top_neg}</div></div>',
    unsafe_allow_html=True,
)
ins3.markdown(
    f'<div class="insight-card insight-blue">'
    f'<div class="insight-label">{t("positive_rate_label", L)}</div>'
    f'<div class="insight-value">📊 {pos_rate:.0%}</div></div>',
    unsafe_allow_html=True,
)

# ── Raw data ───────────────────────────────────────────────────────
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
with st.expander(f"🗂 {t('raw_data', L)}", expanded=False):
    avail = ["model","content","score","cat_label","sentiment","key_point","src_label","creation_time"]
    show  = [c for c in avail if c in fdf.columns]
    st.dataframe(
        fdf[show].rename(columns={"cat_label": t("category",L), "src_label": "Source/来源",
                                   "sentiment": t("sentiment",L)}),
        use_container_width=True, height=380,
    )
    st.download_button(
        f"⬇️ {t('download', L)}",
        fdf.to_csv(index=False, encoding="utf-8-sig"),
        "apple_voc.csv", "text/csv",
    )

# ── Footer ──────────────────────────────────────────────────────────
st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#475569;font-size:0.78rem'>"
    "Built by <a href='https://medium.com/@yulianiu' style='color:#6366f1'>Yuyu</a> · "
    "<a href='https://github.com/HiYulia/apple-voc' style='color:#6366f1'>GitHub</a> · "
    "Data for research purposes only"
    "</div>",
    unsafe_allow_html=True,
)

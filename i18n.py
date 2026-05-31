STRINGS = {
    "title": {
        "zh": "Apple 产品 VOC 分析看板",
        "en": "Apple Product VOC Analytics Dashboard",
    },
    "subtitle": {
        "zh": "数据来源：小红书 · B站 · 京东（持续更新）",
        "en": "Sources: Xiaohongshu · Bilibili · JD.com (continuously updated)",
    },
    "filter_header": {"zh": "筛选", "en": "Filters"},
    "filter_product": {"zh": "产品线", "en": "Product Line"},
    "filter_sentiment": {"zh": "情感", "en": "Sentiment"},
    "filter_source": {"zh": "数据来源", "en": "Data Source"},
    "all": {"zh": "全部", "en": "All"},
    "overview": {"zh": "概览", "en": "Overview"},
    "total_reviews": {"zh": "评论总数", "en": "Total Reviews"},
    "positive_rate": {"zh": "正面占比", "en": "Positive Rate"},
    "negative_rate": {"zh": "负面占比", "en": "Negative Rate"},
    "neutral_rate": {"zh": "中性占比", "en": "Neutral Rate"},
    "date_range": {"zh": "数据时间跨度", "en": "Date Range"},
    "top_concerns": {"zh": "用户最关注什么？", "en": "Top User Concerns"},
    "sentiment_dist": {"zh": "情感分布", "en": "Sentiment Distribution"},
    "category_pie": {"zh": "关注点占比", "en": "Concern Breakdown"},
    "neg_issues": {"zh": "差评核心问题 Top 10", "en": "Top 10 Negative Issues"},
    "no_neg": {"zh": "当前筛选条件下无差评数据", "en": "No negative reviews under current filters"},
    "key_insights": {"zh": "关键洞察", "en": "Key Insights"},
    "top_positive": {"zh": "最受好评维度", "en": "Most Praised Aspect"},
    "top_negative": {"zh": "最多差评维度", "en": "Most Criticized Aspect"},
    "positive_rate_label": {"zh": "好评率", "en": "Positive Rate"},
    "raw_data": {"zh": "查看原始评论", "en": "Browse Raw Reviews"},
    "download": {"zh": "下载当前筛选数据 CSV", "en": "Download Filtered CSV"},
    "data_info": {"zh": "数据说明", "en": "Data Info"},
    "count": {"zh": "评论数", "en": "Count"},
    "category": {"zh": "反馈类别", "en": "Category"},
    "source_label": {"zh": "数据来源分布", "en": "Source Breakdown"},
    "sentiment": {"zh": "情感", "en": "Sentiment"},
    "issue": {"zh": "问题描述", "en": "Issue"},
    # category labels
    "cat_battery": {"zh": "续航电池", "en": "Battery"},
    "cat_camera": {"zh": "拍照摄像", "en": "Camera"},
    "cat_screen": {"zh": "屏幕显示", "en": "Screen"},
    "cat_performance": {"zh": "性能流畅", "en": "Performance"},
    "cat_design": {"zh": "外观设计", "en": "Design"},
    "cat_price_value": {"zh": "价格性价比", "en": "Price/Value"},
    "cat_software": {"zh": "系统软件", "en": "Software"},
    "cat_after_sales": {"zh": "售后服务", "en": "After-sales"},
    "cat_purchase_decision": {"zh": "选机决策", "en": "Purchase Decision"},
    "cat_general_positive": {"zh": "正面体验", "en": "General Positive"},
    "cat_general_negative": {"zh": "负面体验", "en": "General Negative"},
    "cat_other": {"zh": "其他", "en": "Other"},
    # source labels
    "src_xhs_comment": {"zh": "小红书评论", "en": "XHS Comments"},
    "src_xhs_note": {"zh": "小红书笔记", "en": "XHS Notes"},
    "src_bilibili": {"zh": "B站评论", "en": "Bilibili Comments"},
    "src_jd": {"zh": "京东评论", "en": "JD Reviews"},
}


def t(key: str, lang: str) -> str:
    return STRINGS.get(key, {}).get(lang, key)


def cat_label(cat: str, lang: str) -> str:
    return t(f"cat_{cat}", lang)


def src_label(sku: str, lang: str) -> str:
    if sku.startswith("xhs_comment"):
        return t("src_xhs_comment", lang)
    if sku.startswith("xhs_note"):
        return t("src_xhs_note", lang)
    if sku == "bilibili":
        return t("src_bilibili", lang)
    return t("src_jd", lang)

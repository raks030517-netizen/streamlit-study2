# BASIC

import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_marketing():
    df = pd.read_csv('data/marketing_campaign_dataset.csv')
    df['Acquisition_Cost'] = (
        df['Acquisition_Cost']
        .str.replace('[$,]', '', regex=True)
        .astype(float)
    )
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_marketing().copy()
st.title("📣 마케팅 캠페인 대시보드")
st.write(f"전체 데이터: {len(df):,}행")

with st.sidebar:
    st.header("필터")
    if st.button("필터 초기화"):
        st.session_state['campaign_types'] = df['Campaign_Type'].unique().tolist()
        st.session_state['location'] = "전체"

    campaign_types = st.multiselect(
        "캠페인 유형",
        df['Campaign_Type'].unique().tolist(),
        default=st.session_state.get('campaign_types', df['Campaign_Type'].unique().tolist()),
        key='campaign_types'
    )
    location = st.selectbox(
        "지역",
        ["전체"] + sorted(df['Location'].unique().tolist()),
        key='location'
    )

filtered = df[df['Campaign_Type'].isin(campaign_types)]
if location != "전체":
    filtered = filtered[filtered['Location'] == location]

# =========================
# 보고서형 대시보드 스타일
# =========================
st.markdown("""
<style>
.kpi-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 8px;
}
.kpi-title {
    font-size: 14px;
    color: #6b7280;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 34px;
    font-weight: 800;
    color: #111827;
}
.summary-box {
    background: linear-gradient(135deg, #eef6ff, #f8fbff);
    border-left: 8px solid #2563eb;
    padding: 18px 20px;
    border-radius: 16px;
    margin: 10px 0 18px 0;
}
.rank-good {
    background: #ecfdf3;
    border: 1px solid #a7f3d0;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.rank-bad {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 14px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.small-note {
    color: #6b7280;
    font-size: 13px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 요약 지표 계산
# =========================
avg_roi = filtered["ROI"].mean()
avg_conversion = filtered["Conversion_Rate"].mean()
total_campaigns = len(filtered)
avg_cost = filtered["Acquisition_Cost"].mean()

roi_by_type = (
    filtered.groupby("Campaign_Type")["ROI"]
    .mean()
    .sort_values(ascending=False)
)

conv_by_type = (
    filtered.groupby("Campaign_Type")["Conversion_Rate"]
    .mean()
    .sort_values(ascending=False)
)

roi_type_df = roi_by_type.reset_index()
roi_type_df.columns = ["Campaign_Type", "ROI"]

location_summary = (
    filtered.groupby("Location")[["ROI", "Conversion_Rate"]]
    .mean()
    .reset_index()
    .sort_values("ROI", ascending=False)
)

location_summary["순위"] = range(1, len(location_summary) + 1)

monthly = filtered.copy()
monthly["Month"] = monthly["Date"].dt.to_period("M").astype(str)

monthly_summary = (
    monthly.groupby("Month")[["ROI", "Conversion_Rate"]]
    .mean()
    .reset_index()
)

top10 = filtered.sort_values("ROI", ascending=False).head(10)
low10 = filtered.sort_values("ROI", ascending=True).head(10)

best_type = roi_by_type.idxmax()
best_type_roi = roi_by_type.max()

worst_type = roi_by_type.idxmin()
worst_type_roi = roi_by_type.min()

best_location = location_summary.iloc[0]["Location"]
best_location_roi = location_summary.iloc[0]["ROI"]

worst_location = location_summary.iloc[-1]["Location"]
worst_location_roi = location_summary.iloc[-1]["ROI"]

# =========================
# KPI 카드
# =========================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">총 캠페인 수</div>
        <div class="kpi-value">{total_campaigns:,}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">평균 ROI</div>
        <div class="kpi-value">{avg_roi:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">평균 전환율</div>
        <div class="kpi-value">{avg_conversion:.1%}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">평균 획득 비용</div>
        <div class="kpi-value">${avg_cost:,.0f}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================
# 대표님용 한 줄 요약
# =========================
st.markdown("## 📌 Executive Summary")
st.markdown(f"""
<div class="summary-box">
현재 선택된 데이터 기준 <b>평균 ROI는 {avg_roi:.2f}</b>, <b>평균 전환율은 {avg_conversion:.1%}</b>입니다.<br><br>
가장 성과가 좋은 캠페인 유형은 <b>{best_type}</b> (<b>{best_type_roi:.2f}</b>)이며,
가장 낮은 캠페인 유형은 <b>{worst_type}</b> (<b>{worst_type_roi:.2f}</b>)입니다.<br><br>
지역 기준으로는 <b>{best_location}</b>의 평균 ROI가 가장 높고 (<b>{best_location_roi:.2f}</b>),
<b>{worst_location}</b>이 가장 낮습니다 (<b>{worst_location_roi:.2f}</b>).<br><br>
→ 따라서 현재 데이터에서는 <b>캠페인 유형별 차이는 크지 않지만, 지역/기간/비용 조건을 함께 봐야 의사결정에 더 유의미</b>합니다.
</div>
""", unsafe_allow_html=True)

# =========================
# 탭 구성
# =========================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏆 캠페인 요약",
    "📈 월별 추이",
    "🌍 지역 분석",
    "💰 비용 효율"
])

# =========================
# TAB 1: 캠페인 요약
# =========================
with tab1:
    left, right = st.columns([1.4, 1])

    with left:
        st.subheader("캠페인 유형별 평균 ROI 순위")

        fig_type = px.bar(
            roi_type_df.sort_values("ROI", ascending=True),
            x="ROI",
            y="Campaign_Type",
            orientation="h",
            color="ROI",
            color_continuous_scale=["#dbeafe", "#60a5fa", "#1d4ed8"],
            title="캠페인 유형별 평균 ROI"
        )
        fig_type.update_traces(
            texttemplate="%{x:.2f}",
            textposition="outside"
        )
        fig_type.update_layout(
            coloraxis_showscale=False,
            xaxis_title="평균 ROI",
            yaxis_title="",
            title_x=0.02
        )
        st.plotly_chart(fig_type, use_container_width=True)

    with right:
        st.subheader("한눈에 보는 순위")

        top3 = roi_by_type.head(3)
        medals = ["🥇", "🥈", "🥉"]

        for i, (name, value) in enumerate(top3.items()):
            st.markdown(f"""
            <div class="rank-good">
                <b>{medals[i]} {i+1}위</b> — {name}<br>
                평균 ROI: <b>{value:.2f}</b>
            </div>
            """, unsafe_allow_html=True)

        bottom3 = roi_by_type.tail(3).sort_values()

        for i, (name, value) in enumerate(bottom3.items(), start=1):
            st.markdown(f"""
            <div class="rank-bad">
                <b>⚠ 하위 {i}</b> — {name}<br>
                평균 ROI: <b>{value:.2f}</b>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("ROI 상위 / 하위 캠페인")

    c1, c2 = st.columns(2)

    with c1:
        st.write("ROI TOP 10")
        st.dataframe(
            top10[["Campaign_ID", "Company", "Campaign_Type", "Location", "ROI", "Conversion_Rate", "Acquisition_Cost"]],
            use_container_width=True,
            hide_index=True
        )

    with c2:
        st.write("ROI LOW 10")
        st.dataframe(
            low10[["Campaign_ID", "Company", "Campaign_Type", "Location", "ROI", "Conversion_Rate", "Acquisition_Cost"]],
            use_container_width=True,
            hide_index=True
        )

    with st.expander("캠페인 유형별 상세 통계 보기"):
        stats_df = (
            filtered.groupby("Campaign_Type")["ROI"]
            .agg(["count", "mean", "min", "max", "std"])
            .reset_index()
        )
        st.dataframe(stats_df, use_container_width=True, hide_index=True)

# =========================
# TAB 2: 월별 추이
# =========================
with tab2:
    st.subheader("월별 성과 추이")

    fig_month_roi = px.line(
        monthly_summary,
        x="Month",
        y="ROI",
        markers=True,
        title="월별 평균 ROI 추이"
    )
    fig_month_roi.update_traces(line_color="#2563eb", line_width=3, marker_size=8)
    fig_month_roi.update_layout(title_x=0.02, xaxis_title="", yaxis_title="ROI")
    st.plotly_chart(fig_month_roi, use_container_width=True)

    fig_month_conv = px.line(
        monthly_summary,
        x="Month",
        y="Conversion_Rate",
        markers=True,
        title="월별 평균 전환율 추이"
    )
    fig_month_conv.update_traces(line_color="#10b981", line_width=3, marker_size=8)
    fig_month_conv.update_layout(title_x=0.02, xaxis_title="", yaxis_title="Conversion Rate")
    st.plotly_chart(fig_month_conv, use_container_width=True)

    best_month_row = monthly_summary.loc[monthly_summary["ROI"].idxmax()]
    worst_month_row = monthly_summary.loc[monthly_summary["ROI"].idxmin()]

    st.info(
        f"가장 성과가 좋았던 달은 **{best_month_row['Month']}** (평균 ROI **{best_month_row['ROI']:.2f}**)이며, "
        f"가장 낮았던 달은 **{worst_month_row['Month']}** (평균 ROI **{worst_month_row['ROI']:.2f}**)입니다."
    )

# =========================
# TAB 3: 지역 분석
# =========================
with tab3:
    st.subheader("지역별 성과 분석")

    fig_location = px.bar(
        location_summary.sort_values("ROI", ascending=True),
        x="ROI",
        y="Location",
        orientation="h",
        color="ROI",
        color_continuous_scale=["#dcfce7", "#4ade80", "#15803d"],
        title="지역별 평균 ROI 순위"
    )
    fig_location.update_traces(
        texttemplate="%{x:.2f}",
        textposition="outside"
    )
    fig_location.update_layout(
        coloraxis_showscale=False,
        xaxis_title="평균 ROI",
        yaxis_title="",
        title_x=0.02
    )
    st.plotly_chart(fig_location, use_container_width=True)

    rank_view = location_summary[["순위", "Location", "ROI", "Conversion_Rate"]].copy()
    rank_view.columns = ["순위", "지역", "평균 ROI", "평균 전환율"]

    st.dataframe(rank_view, use_container_width=True, hide_index=True)

    st.markdown("### 🔥 캠페인 유형 × 지역 ROI 히트맵")

    heatmap_data = (
        filtered.groupby(["Campaign_Type", "Location"])["ROI"]
        .mean()
        .reset_index()
    )

    fig_heatmap = px.density_heatmap(
        heatmap_data,
        x="Location",
        y="Campaign_Type",
        z="ROI",
        color_continuous_scale=["#eff6ff", "#60a5fa", "#1d4ed8"],
        title="캠페인 유형과 지역별 평균 ROI"
    )
    fig_heatmap.update_layout(title_x=0.02)
    st.plotly_chart(fig_heatmap, use_container_width=True)

# =========================
# TAB 4: 비용 효율
# =========================
with tab4:
    st.subheader("광고비 대비 ROI 분석")

    # 20만 건 전체를 뿌리면 너무 빽빽하므로 표본만 사용
    sample_df = filtered.sample(min(len(filtered), 5000), random_state=42)

    fig_cost_roi = px.scatter(
        sample_df,
        x="Acquisition_Cost",
        y="ROI",
        color="Campaign_Type",
        opacity=0.45,
        hover_data=["Campaign_ID", "Company", "Location", "Conversion_Rate"],
        title="광고비와 ROI의 관계 (표본 5,000건)"
    )
    fig_cost_roi.update_layout(title_x=0.02)
    st.plotly_chart(fig_cost_roi, use_container_width=True)

    cost_threshold = filtered["Acquisition_Cost"].quantile(0.8)
    roi_threshold = filtered["ROI"].quantile(0.2)

    inefficient = (
        filtered[
            (filtered["Acquisition_Cost"] >= cost_threshold) &
            (filtered["ROI"] <= roi_threshold)
        ]
        .sort_values(["Acquisition_Cost", "ROI"], ascending=[False, True])
        .head(10)
    )

    st.warning(
        "광고비는 높지만 ROI가 낮은 캠페인은 비용 효율 개선이 필요한 우선 점검 대상입니다."
    )

    st.write("비용 대비 비효율 캠페인 TOP 10")
    st.dataframe(
        inefficient[["Campaign_ID", "Company", "Campaign_Type", "Location", "Acquisition_Cost", "ROI", "Conversion_Rate"]],
        use_container_width=True,
        hide_index=True
    )
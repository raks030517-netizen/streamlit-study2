# CHALLENGE

import streamlit as st
import pandas as pd

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


st.subheader("🔍 키워드 검색")
st.caption("회사명, 지역, 캠페인 유형, 채널명 등을 입력하면 관련 데이터를 바로 검색합니다.")

keyword = st.text_input("키워드 검색", placeholder="예: Chicago, Email, TechCorp")

if keyword:
    mask = df.apply(
        lambda row: keyword.lower() in str(row).lower(),
        axis=1
    )

    search_result = df[mask]

    st.success(f"'{keyword}' 검색 결과: {len(search_result):,}행")

    st.dataframe(
        search_result.head(50),
        use_container_width=True
    )
else:
    st.info("검색어를 입력하면 결과가 표시됩니다.")

st.divider()
uploaded = st.file_uploader("내 데이터 업로드 (CSV)", type=["csv"])
if uploaded is not None:
    user_df = pd.read_csv(uploaded)
    st.success(f"{uploaded.name} ({len(user_df):,}행)")
    st.dataframe(user_df.describe())
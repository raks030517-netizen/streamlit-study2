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

with st.form("search_form"):
    keyword   = st.text_input("키워드 검색")
    submitted = st.form_submit_button("검색")

if submitted and keyword:
    mask    = df.apply(lambda row: keyword.lower() in str(row).lower(), axis=1)
    filtered = df[mask]
    st.write(f"'{keyword}' 검색 결과: {len(filtered):,}행")
    st.dataframe(filtered.head(20))

st.divider()
uploaded = st.file_uploader("내 데이터 업로드 (CSV)", type=["csv"])
if uploaded is not None:
    user_df = pd.read_csv(uploaded)
    st.success(f"{uploaded.name} ({len(user_df):,}행)")
    st.dataframe(user_df.describe())
# 진입점 entry point
# import streamlit as st

# Page
# home = st.Page("home.py", title="홈", icon="🖤")
# dashboard = st.Page("dashboard.py", title="대시보드")

# Navigation
# pg = st.navigation([home, dashboard])
# pg.run()


import streamlit as st
overview = st.Page("session1.py", title="요약", icon="📊")
detail   = st.Page("session2.py", title="상세 분석", icon="🔍")
setting = st.Page("session3.py", title="설정")

pg = st.navigation({"분석": [overview, detail], "설정": [setting]})
pg.run()

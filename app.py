# APPLIED

import streamlit as st
overview = st.Page("overview.py", title="요약",     icon="📊")
detail   = st.Page("detail.py",   title="상세 분석", icon="🔍")
pg = st.navigation([overview, detail])
pg.run()
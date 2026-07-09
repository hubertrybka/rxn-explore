import streamlit as st

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    c1 = st.container(border=False, width=600)
    with c1:
        st.image('data/imgs/the_team.jpg', width=1536)
    if st.button("🥳 **Click to make them party** 🥳", type="secondary", width='stretch'):
        st.balloons()

st.info("This page is under construction")
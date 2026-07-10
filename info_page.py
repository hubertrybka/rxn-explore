import streamlit as st

col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.space("small")
    c1 = st.container(border=False, width=600)
    with c1:
        st.image("data/imgs/the_team.jpg", width=1536)
    st.space("small")
    if st.button(
        "🥳 Click here to make them party 🥳", type="primary", width="stretch"
    ):
        st.balloons()
    st.info("This page is under construction", icon='🛠️')
import streamlit as st
import pathlib

if 'data_dir' not in st.session_state:
    # initialize session state
    st.session_state['dataset'] = None
    st.session_state['dataset_name'] = None
    st.session_state['molecule'] = None
    st.session_state['data_dir'] = pathlib.Path().cwd() / 'data' / 'users'
    st.session_state['favourite_idcs'] = []

st.title("rxn-explore")



pg = st.navigation([
    st.Page("data_page.py", title="Load Data", icon="💾"),
    st.Page("molecules_page.py", title="Browse Molecules", icon="👁"),
    st.Page("favourites_page.py", title="Favourites", icon="⭐"),
])

pg.run()


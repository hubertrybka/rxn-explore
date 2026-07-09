import streamlit as st
import pathlib
import datetime

if 'data_dir' not in st.session_state:
    # Initialize session state
    st.session_state['dataset'] = None
    st.session_state['dataset_name'] = None
    st.session_state['molecule'] = None
    st.session_state['data_dir'] = pathlib.Path().cwd() / 'data' / 'library'
    st.session_state['user_report_dir'] = pathlib.Path().cwd() / 'data' / 'user_reports'
    st.session_state['favourite_idcs'] = []
    st.session_state['bugged_idcs'] = []
    st.session_state['view_index'] = 0
    st.set_page_config(page_title="rxn-explore",
                       page_icon=":heart_decoration:",
                       layout="wide")
    # make sure the directories are there
    st.session_state['data_dir'].mkdir(parents=True, exist_ok=True)
    st.session_state['user_report_dir'].mkdir(parents=True, exist_ok=True)

logo_col1, logo_col2 = st.columns([2, 1])
st.image('data/imgs/header_logo.png', width=800)

# Display info about the loaded dataset
if st.session_state['dataset'] is not None:
    st.success(f"Dataset: {st.session_state['dataset_name']} ({st.session_state['dataset'].n_molecules} molecules)", icon="✅")

# Display a list of datasets saved locally
with st.sidebar:
    cont_lib = st.container(border=True, width='stretch')
    with cont_lib:
        st.subheader("📚 Recently added to library:")
        library_files = sorted(
            st.session_state['data_dir'].glob('*.pkl'),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )[:10]
        if library_files:
            to_display = []
            for f in library_files:
                uploaded_at = datetime.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                to_display.append(f"* **{f.stem}** `{uploaded_at}`  ")
            st.markdown("\n".join(to_display))
        else:
            st.caption("No datasets in library")

# Define the navigation menu
pg = st.navigation([
    st.Page("data_page.py", title="Load Data", icon="💾"),
    st.Page("molecules_page.py", title="Browse Molecules", icon="👁"),
    st.Page("favourites_page.py", title="Favourites", icon="⭐"),
    st.Page("info_page.py", title="Info", icon="ℹ️")
], position="sidebar")

pg.run()

st.caption("2026 Hubert Rybka • for the fearless synthetic chemists of IPPAS • never surrender")
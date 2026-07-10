import datetime
import pathlib

from src.utils import sort_library
import streamlit as st


def init_session_state():
    st.session_state["dataset"] = None
    st.session_state["dataset_name"] = None
    st.session_state["data_dir"] = pathlib.Path().cwd() / "data" / "library"
    st.session_state["user_report_dir"] = pathlib.Path().cwd() / "data" / "user_reports"
    st.session_state["favourite_idcs"] = []
    st.session_state["bugged_idcs"] = []
    st.session_state["view_index"] = 0
    st.set_page_config(
        page_title="rxn-explore", page_icon=":heart_decoration:", layout="wide"
    )
    # make sure the directories are there
    st.session_state["data_dir"].mkdir(parents=True, exist_ok=True)
    st.session_state["user_report_dir"].mkdir(parents=True, exist_ok=True)
    st.session_state["lib_max_entries"] = 100


def display_library_contents() -> bool:
    cont_lib = st.container(border=True, width="stretch", horizontal_alignment="left")
    with cont_lib:
        st.header("📚 Library", text_alignment="center")
        sort_name_map = {
            "date (newest)": "**by date** (_newest_)",
            "date (oldest)": "**by date** (_oldest_)",
            "name (A→Z)": "**by name** (_A → Z_)",
            "name (Z→A)": "**by name** (_Z → A_)",
        }
        library_files = list(st.session_state["data_dir"].glob("*.pkl"))
        num_mols_to_display = min(
            st.session_state.get("lib_entries_to_display", 10), len(library_files)
        )
        popover_text = (
            "**Showing** "
            + f"(_{num_mols_to_display}/{len(library_files)}_) "
            + sort_name_map[st.session_state.get("lib_sort_by", "date (newest)")]
        )

        with st.popover(popover_text, type="secondary", use_container_width=True):
            st.selectbox(
                "**Sort** entries by:",
                ["name (A→Z)", "name (Z→A)", "date (newest)", "date (oldest)"],
                key="lib_sort_by",
                index=2,
            )
            st.selectbox(
                "**Number** of entries to display:",
                [10, 20, 50, 100],
                key="lib_entries_to_display",
                index=0,
            )

        if library_files:
            sorted_library = sort_library(library_files)[
                : st.session_state.get("lib_entries_to_display", 10)
            ]
            to_display = []
            for f in sorted_library:
                uploaded_at = datetime.datetime.fromtimestamp(
                    f.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M")
                to_display.append(f"- **{f.stem}** `{uploaded_at}`  ")
            st.markdown("\n".join(to_display))
            return True
        else:
            st.caption("No datasets in library")
            return False


# ========================================================================#

if "data_dir" not in st.session_state:
    init_session_state()

_, col_logo, _ = st.columns([1, 10, 1])
with col_logo:
    st.image("data/imgs/header_logo.png", width="stretch")


# Display a list of datasets saved locally
with st.sidebar:
    # Display info about the loaded dataset
    c_data = st.container(border=False, width="stretch", horizontal_alignment="center")
    with c_data:
        if st.session_state["dataset"] is not None:
            st.success(
                f"**Dataset loaded** | {st.session_state['dataset_name']}\
                 _({st.session_state['dataset'].n_molecules} rows)_",
                icon="✅",
            )
        else:
            st.info(
                """**Dataset not loaded**. Navigate to _Load Data_ page and select a data file to start""",
                icon="⚠️",
            )
    display_library_contents()


# Define the navigation menu
pg = st.navigation(
    [
        st.Page("data_page.py", title="Load Data", icon="💾"),
        st.Page("molecules_page.py", title="Browse Molecules", icon="👁"),
        st.Page("favourites_page.py", title="Favourites", icon="⭐"),
        st.Page("info_page.py", title="Info", icon="ℹ️"),
    ],
    position="sidebar",
)

pg.run()

st.caption(
    "2026 Hubert Rybka • for the fearless synthetic chemists of IPPAS • never surrender"
)

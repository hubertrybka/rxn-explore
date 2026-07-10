import streamlit as st

from src.data import MoleculeDataset
from src.utils import list_library


@st.cache_resource(show_spinner=False)
def _load_dataset(path_or_file, data_dir, from_pkl: bool) -> MoleculeDataset:
    dataset = MoleculeDataset([], data_dir)
    dataset.load(path_or_file, from_pkl=from_pkl)
    return dataset


def set_session_state(dataset, filename):
    name = filename.replace(".csv", "") if filename.endswith(".csv") else filename
    st.session_state["dataset"] = dataset
    st.session_state["dataset_name"] = name
    st.success("Data loaded successfully")
    st.rerun()


def upload_file():
    st.subheader("⬆️ Upload file")
    st.caption("Upload a .csv file from your machine")
    uploaded_file = st.file_uploader(
        "",
        accept_multiple_files=False,
        type=".csv",
        label_visibility="collapsed",
        max_upload_size=100,
    )
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("Upload data", use_container_width=True):
            if uploaded_file is None:
                return False
            else:
                with st.spinner("Loading...", show_time=False):
                    dataset = _load_dataset(
                        uploaded_file, st.session_state["data_dir"], from_pkl=False
                    )
                    set_session_state(dataset, uploaded_file.name)
                    return True


def load_file():
    st.subheader("💾 Load from library")
    st.caption("Load a dataset which has been previously saved to the library")
    st.space(size="small")
    datasets = list_library(st.session_state["data_dir"], suffix=False)
    name = st.selectbox("", datasets, index=None, label_visibility="collapsed")
    dataset_path = st.session_state["data_dir"] / f"{name}.pkl"
    _, col, _ = st.columns([1, 2, 1])
    with col:
        if st.button("Load data", use_container_width=True):
            if name is None:
                return False
            else:
                with st.spinner("Loading...", show_time=False):
                    dataset = _load_dataset(
                        dataset_path, st.session_state["data_dir"], from_pkl=True
                    )
                    set_session_state(dataset, name)
                    return True


def save_dataset():
    st.subheader("📚 Save to library")
    st.caption("Store data on the server to access it quickly in future sessions")
    filename = st.text_input(
        "Save as:",
        value=(
            st.session_state["dataset_name"] if st.session_state["dataset_name"] else ""
        ),
    )
    if st.button("Add to library"):
        data_dir = st.session_state["data_dir"]
        if st.session_state["dataset"] is None:
            # if no data is loaded, do nothing
            st.error("No data to save - upload a dataset first", icon="❌")
            return
        if not filename:
            # if no filename is provided, do nothing
            st.error("Please enter a name for the dataset", icon="❌")
            return
        if len(list_library(data_dir)) >= 100:
            st.error(
                f"**ERROR: Maximum allowed number of datasets stored in library ({st.session_state["lib_max_entries"]}) "
                f"has been reached**. Remove old files from server storage before adding new ones. The "
                f"files saved to library are stored in `{data_dir}`.",
                icon="❌",
            )
            return
        try:
            st.session_state["dataset"].save(filename)
            list_library.clear()
            st.success(f"{filename} added to library")
        except Exception as e:
            st.error(e, icon="❌")


# ========================================================================#

st.header("Load Data", text_alignment="center")
st.markdown(
    "Upload new .csv data file or load existing one from server storage",
    text_alignment="center",
)

st.divider()

# Uploading

col1, col_2, col3 = st.columns([5.5, 1, 6])

with col1:
    c_upload = st.container(border=True, height=360)
    with c_upload:
        if upload_file() is False:
            st.error("Please select a file to upload", icon="❌")

with col_2:
    c_or = st.container(
        border=False,
        vertical_alignment="center",
        horizontal_alignment="center",
        height=360,
    )
    with c_or:
        st.markdown("## OR", text_alignment="center")

# Reading from disk
with col3:
    c_read = st.container(border=True, height=360)
    with c_read:
        if load_file() is False:
            st.error("Please select a dataset from the dropdown list", icon="❌")

# Allow the user to save uploaded data to disk
st.space(size="small")
c_save = st.container(border=True)
with c_save:
    save_dataset()

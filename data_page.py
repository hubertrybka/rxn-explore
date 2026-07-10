import streamlit as st
from src.data import MoleculeDataset
from src.utils import list_library
from src.streamlit import render_user_guide, file_upload_error, load_from_library_error, library_full_error


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
        "Select file",
        accept_multiple_files=False,
        type=".csv",
        label_visibility="collapsed",
        max_upload_size=100
    )
    if st.button("Upload data", use_container_width=True, disabled=uploaded_file is None, type="primary"):
        with st.spinner("Loading...", show_time=False, width='stretch'):
            try:
                # Load the dataset from the uploaded file
                dataset = _load_dataset(uploaded_file, st.session_state["data_dir"], from_pkl=False)
                set_session_state(dataset, uploaded_file.name)
            except Exception as e:
                # Show a popup with the error message
                file_upload_error(e)

def load_file():
    st.subheader("💾 Load from library")
    st.caption("Load a dataset from server storage")
    st.space(size="small")
    datasets = list_library(st.session_state["data_dir"], suffix=False)
    name = st.selectbox("Select", datasets, index=None, label_visibility="collapsed", placeholder="Select from library")
    dataset_path = st.session_state["data_dir"] / f"{name}.pkl"
    if st.button("Load data", use_container_width=True, disabled=name is None, type="primary"):
        with st.spinner("Loading...", show_time=False, width='stretch'):
            try:
                # Load the dataset from the selected file
                dataset = _load_dataset(dataset_path, st.session_state["data_dir"], from_pkl=True)
                set_session_state(dataset, name)
            except Exception as e:
                # Show a popup with the error message
                load_from_library_error(e)

def save_dataset():
    st.subheader("Save to library")
    st.caption("Store data to server storage - access it quickly in future sessions")
    filename = st.text_input(
        "Save as:",
        value=(
            st.session_state["dataset_name"] if st.session_state["dataset_name"] else ""
        ),
    )
    col1_save, col2_save = st.columns([1, 1], vertical_alignment="top", gap="small")
    if st.session_state["saved_to_library"]:
        with col2_save:
            st.success(f"Dataset saved to library", icon="✅")
        st.session_state["saved_to_library"] = False
    with col1_save:
        add_to_lib = st.button("Add to library", use_container_width=True, disabled=st.session_state["dataset"] is None)
    if add_to_lib:
        # Check if the user has entered a filename
        if not filename:
            with col2_save:
                st.error("Please enter a name for the dataset", icon="❌")
            return
        # Check if the library is full
        if len(list_library(st.session_state['data_dir'])) >= 100:
            library_full_error()
            return
        try:
            st.session_state["dataset"].save(filename)
            list_library.clear()
            with col2_save:
                st.success(f"Dataset saved to library", icon="✅")
                st.session_state["saved_to_library"] = True
                st.rerun()
        except Exception as e:
            with col2_save:
                st.error(e, icon="❌")


# ========================================================================#

st.header("Load your data to the server", text_alignment="center")
st.markdown(
    "Before you use this app - get familiar with the **user guide** below:",
    text_alignment="center",
)

render_user_guide()

st.divider()

# Uploading

col1, col_2, col3 = st.columns([5.5, 1, 6])

with col1:
    c_upload = st.container(border=True, height=350, horizontal_alignment="center")
    with c_upload:
        upload_file()

with col_2:
    c_or = st.container(
        border=False,
        vertical_alignment="center",
        horizontal_alignment="center",
        height=350,
    )
    with c_or:
        st.markdown("### OR", text_alignment="center")

# Reading from disk
with col3:
    c_read = st.container(border=True, height=350, horizontal_alignment="center")
    with c_read:
        load_file()

# Allow the user to save uploaded data to disk
st.space(size="small")
c_save = st.container(border=True)
with c_save:
    save_dataset()
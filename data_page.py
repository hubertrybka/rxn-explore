import streamlit as st
from src.data import MoleculeDataset
from src.utils import list_library, retrieve_timestamp

@st.cache_resource(show_spinner=False)
def _load_dataset(path_or_file, data_dir, from_pkl: bool) -> MoleculeDataset:
    dataset = MoleculeDataset([], data_dir)
    dataset.load(path_or_file, from_pkl=from_pkl)
    return dataset

def upload_file():
    st.subheader("Upload file")
    uploaded_file = st.file_uploader('',
                                     accept_multiple_files=False,
                                     help="only .csv files are allowed")
    if st.button("Upload file") and uploaded_file is not None:
        with st.spinner("Loading...", show_time=False):
            dataset = _load_dataset(uploaded_file, st.session_state['data_dir'], from_pkl=False)
            st.session_state['dataset'] = dataset
            st.session_state['dataset_name'] = uploaded_file.name.replace('.csv', '')
            st.success("Data loaded successfully")
            st.rerun()

def load_file():
    st.subheader("Load from library")
    datasets = list_library(st.session_state['data_dir'], suffix=False)
    datasets.sort(key=retrieve_timestamp, reverse=True)
    name = st.selectbox("Select dataset", datasets)
    dataset_path = st.session_state['data_dir'] / f"{name}.pkl"
    if st.button("Load data") and name is not None:
        with st.spinner("Loading...", show_time=False):
            dataset = _load_dataset(dataset_path, st.session_state['data_dir'], from_pkl=True)
            st.session_state['dataset'] = dataset
            st.session_state['dataset_name'] = name
            st.success("Data loaded successfully")
            st.rerun()

def save_dataset():
    st.subheader("Save dataset to library 📚")
    filename = st.text_input("Dataset name")
    if st.button("Add to library") and filename:
        try:
            st.session_state['dataset'].save(filename)
            list_library.clear()
            st.success(f"{filename} added to library")
            st.rerun()
        except Exception as e:
            st.error(e)

if st.session_state['dataset'] is not None:
    st.success(f"✅ Loaded dataset: {st.session_state['dataset_name']} ({st.session_state['dataset'].n_molecules} molecules)")
    st.space(size="small")

# Uploading
c_upload = st.container(border=True)
with c_upload:
    upload_file()

# Reading from disk
c_read = st.container(border=True)
with c_read:
    load_file()

# Allow the user to save uploaded data to disk
st.space(size="small")
c_save = st.container(border=True)
with c_save:
    save_dataset()
import pathlib
import streamlit as st

@st.cache_data(show_spinner=False)
def list_library(data_dir: pathlib.Path, suffix=True) -> list[str]:
    contents = [f.name for f in data_dir.glob('*.pkl')]
    if not suffix:
        contents = [f.replace('.pkl', '') for f in contents]
    contents.sort(key=lambda x: x.split('_')[-1], reverse=True)
    return contents

def retrieve_timestamp(filename):
    return filename.split('_')[-1].replace('.pkl', '')
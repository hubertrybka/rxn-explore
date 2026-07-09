import streamlit as st
from src.data import MoleculeDataset
from src.utils import list_library, retrieve_timestamp

@st.cache_resource(show_spinner=False)
def _load_dataset(path_or_file, data_dir, from_pkl: bool) -> MoleculeDataset:
    dataset = MoleculeDataset([], data_dir)
    dataset.load(path_or_file, from_pkl=from_pkl)
    return dataset

def set_session_state(dataset, filename):
    if filename.endswith('.csv'):
        name = filename.replace('.csv', '')
    else:
        name = filename
    st.session_state['dataset'] = dataset
    st.session_state['dataset_name'] = name
    st.session_state['is_bugged'] = [False] * dataset.n_molecules
    st.success("Data loaded successfully")
    st.rerun()

st.header("Load Data")

with st.expander("**How to use rxn-explore**", icon="📋"):
    st.markdown("""
    This app serves as an interface between a chemist and the output files of the GenProSyn GFlowNet.
    It allows you to browse the generated molecules, visualize their structures and preview synthesis pathways.
    
    ### How to use:
    
    1. **Upload a .csv file** containing the SMILES of the molecules you want to visualize. The file
    should contain at least two columns: "molecule" and "path".  
    You can save an uploaded file to the library (disk) to access it easily in future sessions.
    
    2. **Navigate to "Browse Molecules" page** (from sidebar) to visualize the molecules present in the dataset.
    Each molecule is displayed with its synthetical pathway.  
    You can select promising molecules as "favourite" to access them later.
    
    3. **Navigate to "Favourites" page** (from sidebar) to view the molecules you have marked as favourite.
    Click the eye icon next to a molecule to move it to the "Browse Molecules" page.
    """)
    st.warning("Remember that all session state is cleared when you close the app!")

st.space(size="small")

def upload_file():
    st.subheader("⬆️ Upload file ⬆️")
    st.write("Upload a .csv file from your machine")
    uploaded_file = st.file_uploader('',
                                     accept_multiple_files=False)
    if st.button("Upload file"):
        if uploaded_file is None:
            st.error("Please select a file to upload")
            return
        else:
            with st.spinner("Loading...", show_time=False):
                dataset = _load_dataset(uploaded_file, st.session_state['data_dir'], from_pkl=False)
                set_session_state(dataset, uploaded_file.name)

def load_file():
    st.subheader("💾 Load from library 💾")
    st.write("Load a dataset which has been previously saved to the library")
    datasets = list_library(st.session_state['data_dir'], suffix=False)
    datasets.sort(key=retrieve_timestamp, reverse=True)
    name = st.selectbox("Select dataset", datasets, index=None)
    dataset_path = st.session_state['data_dir'] / f"{name}.pkl"
    if st.button("Load data"):
        if name is None:
            st.error("Please select a dataset from the dropdown list")
            return
        else:
            with st.spinner("Loading...", show_time=False):
                dataset = _load_dataset(dataset_path, st.session_state['data_dir'], from_pkl=True)
                set_session_state(dataset, name)

def save_dataset():
    st.subheader("📚 Save to library 📚")
    st.write("Store data on the server to access it quickly in future sessions")
    filename = st.text_input("Save as:", value=st.session_state['dataset_name'] if st.session_state['dataset_name'] else "")
    if st.button("Add to library"):
        if st.session_state['dataset'] is None:
            # if no data is loaded, do nothing
            st.error("No data to save - upload a dataset first")
            return
        if not filename:
            # if no filename is provided, do nothing
            st.error("Please enter a name for the dataset")
            return
        try:
            st.session_state['dataset'].save(filename)
            list_library.clear()
            st.success(f"{filename} added to library")
            st.rerun()
        except Exception as e:
            st.error(e)

# Uploading

col1, col2 = st.columns([1, 1])

with col1:
    c_upload = st.container(border=True, height=300)
    with c_upload:
        upload_file()

# Reading from disk
with col2:
    c_read = st.container(border=True, height=300)
    with c_read:
        load_file()

# Allow the user to save uploaded data to disk
st.space(size="small")
c_save = st.container(border=True)
with c_save:
    save_dataset()
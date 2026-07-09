import pathlib
import streamlit as st
import rdkit.Chem as Chem
from rdkit.Chem import Descriptors
import rdkit.Chem.QED as QED
import pandas as pd

@st.cache_data(show_spinner=False)
def list_library(data_dir: pathlib.Path, suffix=True) -> list[str]:
    contents = [f.name for f in data_dir.glob('*.pkl')]
    if not suffix:
        contents = [f.replace('.pkl', '') for f in contents]
    contents.sort(key=lambda x: x.split('_')[-1], reverse=True)
    return contents

def retrieve_timestamp(filename):
    return filename.split('_')[-1].replace('.pkl', '')

@st.cache_data(show_spinner=False)
def calculate_descriptors(smiles: str) -> pd.DataFrame:
    """
    Calculate molecular descriptors for a given RDKit molecule.
    Returns a dictionary of descriptor names and their values.
    """
    mol = Chem.MolFromSmiles(smiles)
    descriptor_funcs = {
        'Mol Wt': Descriptors.MolWt,
        'H-bond Donors': Descriptors.NumHDonors,
        'H-bond Acceptors': Descriptors.NumHAcceptors,
        'TPSA': Descriptors.TPSA,
        'cLogP': Descriptors.MolLogP,
        'QED': QED.qed
    }
    values = []
    for name, func in descriptor_funcs.items():
        values.append(func(mol))
    return pd.DataFrame({'Property': list(descriptor_funcs.keys()), 'Value': values})
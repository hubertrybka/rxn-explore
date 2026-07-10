import pathlib

import datetime
import pandas as pd
import rdkit.Chem as Chem
import rdkit.Chem.QED as QED
import streamlit as st
from rdkit.Chem import Descriptors


@st.cache_data(show_spinner=False)
def list_library(data_dir: pathlib.Path, suffix=True) -> list[str]:
    contents = [f.name for f in data_dir.glob("*.pkl")]
    if not suffix:
        contents = [f.replace(".pkl", "") for f in contents]
    contents.sort(key=lambda x: x.split("_")[-1], reverse=True)
    return contents


@st.cache_data(show_spinner=False)
def calculate_descriptors(smiles: str) -> pd.DataFrame:
    """
    Calculate molecular descriptors for a given RDKit molecule.
    Returns a dictionary of descriptor names and their values.
    """
    mol = Chem.MolFromSmiles(smiles)
    descriptor_funcs = {
        "Mol Wt": Descriptors.MolWt,
        "H-bond Donors": Descriptors.NumHDonors,
        "H-bond Acceptors": Descriptors.NumHAcceptors,
        "TPSA": Descriptors.TPSA,
        "cLogP": Descriptors.MolLogP,
        "QED": QED.qed,
    }
    values = [func(mol) for func in descriptor_funcs.values()]
    return pd.DataFrame({"Property": list(descriptor_funcs.keys()), "Value": values})


def get_timestamp():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

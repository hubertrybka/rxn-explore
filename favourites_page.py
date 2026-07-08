import base64
from io import BytesIO

import streamlit as st
import pandas as pd

def image_to_data_url(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"

def prepare_df():
    rows = []
    for i in st.session_state['favourite_idcs']:
        molecule = st.session_state['dataset'].molecules[i]
        row = {"Index": i,
               "SMILES": molecule.get_smiles(),
               "Structure": image_to_data_url(molecule.render_molecule()),
               "Info": ''
               }
        rows.append(row)
    df = pd.DataFrame(rows)
    return df

st.title("Favourites")

if st.session_state['favourite_idcs'] is not None:
    df = prepare_df()
    st.dataframe(df, use_container_width=True, column_config={
        "Index": st.column_config.NumberColumn("Index", help="Index of the molecule in the dataset"),
        "SMILES": st.column_config.TextColumn("SMILES", help="SMILES representation of the molecule", width='small'),
        "Structure": st.column_config.ImageColumn("Structure", help="Rendered structure of the molecule",
                                                  width='medium'),
        "Info": st.column_config.TextColumn("Info", help="Additional info")}, row_height=150)

else:
    st.warning("No compounds added to favourites yet")


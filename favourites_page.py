import base64
from io import BytesIO

import pandas as pd
import streamlit as st
from src.utils import get_timestamp


def image_to_data_url(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{encoded}"


def prepare_df():
    rows = []
    for i in st.session_state["favourite_idcs"]:
        molecule = st.session_state["dataset"].molecules[i]
        row = {
            "Index": i,
            "Structure": image_to_data_url(molecule.render_molecule(as_preview=True)),
            "SMILES": molecule.get_smiles(),
            "Info": "",
            "Pathway": ":material/visibility:",
        }
        rows.append(row)
    df = pd.DataFrame(rows)
    return df


# ========================================================================#

st.header("Favourites", text_alignment="center")
st.markdown(
    "Display a summary of molecules marked as favourite", text_alignment="center"
)
st.divider()

if st.session_state["favourite_idcs"]:

    df = prepare_df()
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "Index": st.column_config.NumberColumn(
                "Index", width=30, alignment="center"
            ),
            "Structure": st.column_config.ImageColumn("Structure", width=200),
            "SMILES": st.column_config.TextColumn("SMILES", width="medium"),
            "Info": st.column_config.TextColumn("Info", width="medium"),
            "Pathway": st.column_config.ButtonColumn(
                "View in Browser", key="fav_clicked", width=50, type="tertiary"
            ),
        },
        row_height=200,
        hide_index=True,
    )

    if st.session_state["fav_clicked"]:
        idx = st.session_state["fav_clicked"]["row"]
        st.session_state["view_index"] = df.iloc[idx]["Index"]
        st.switch_page("molecules_page.py")

    if st.download_button(
        "Download SMILES as .csv",
        df[["Index", "SMILES"]].to_csv(index=False),
        f"fav_{st.session_state['dataset_name']}_{get_timestamp()}.csv",
        type="primary",
    ):
        pass
else:
    st.warning("No molecules marked favourite", icon="⚠️")

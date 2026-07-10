import datetime

import streamlit as st
import yaml

from src.utils import calculate_descriptors


def molecule_selection(dataset):
    st.subheader("Index of the molecule to display")
    st.caption("(molecules are indexed from 0 up)")
    return st.number_input(
        "Select index:",
        min_value=0,
        max_value=dataset.n_molecules - 1,
        value=st.session_state["view_index"],
        step=1,
        width=200,
    )


def handle_pathway_rendering_error(dataset, index, error):
    st.write("**Pathway could not be rendered.** Let me know by sending a report:")

    if st.button(
        "Report", type="primary", disabled=index in st.session_state["bugged_idcs"]
    ):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        molecule_raw = dataset.raw_data.iloc[index]
        filename = f"bug_report_{timestamp}.txt"

        with open(st.session_state["user_report_dir"] / filename, "a") as f:
            comment = str(error).replace("\n", "\n#")
            f.write(f"# Exception: {comment}\n\n")
            yaml_data = yaml.dump(
                molecule_raw.to_dict(), default_flow_style=False, width=50, indent=4
            )
            f.write(yaml_data)
        st.session_state["bugged_idcs"].append(index)
        st.rerun()


def handle_add_to_favourites(index):
    _, col, _ = st.columns([1, 2, 1])
    with col:
        fav = st.button(
            (
                "**Add** to favourites"
                if index not in st.session_state["favourite_idcs"]
                else "**Remove** from favourites"
            ),
            type=(
                "primary"
                if index in st.session_state["favourite_idcs"]
                else "secondary"
            ),
            icon="⭐",
            use_container_width=True,
        )
        if fav:
            if index not in st.session_state["favourite_idcs"]:
                st.session_state["favourite_idcs"].append(index)
            else:
                st.session_state["favourite_idcs"].remove(index)
            st.rerun()


# ========================================================================#

st.header("Browse Molecules", text_alignment="center")
st.markdown("Display molecular structures of the generated ligands and\
 break down their synthesis pathways", text_alignment="center")
st.divider()

if st.session_state["dataset"] is not None:

    # Select a molecule from the dataset by index
    dataset = st.session_state["dataset"]

    # Display the molecule
    left_col, right_col = st.columns([1, 1])
    with left_col:
        index = molecule_selection(dataset)
        molecule = dataset[index]

        # Display calculated properties
        descriptors = calculate_descriptors(molecule.get_smiles())
        st.subheader("Calculated properties")
        st.dataframe(descriptors, width=400, hide_index=True)

    with right_col:
        con_1 = st.container(border=True, width="content")
        with con_1:
            st.image(molecule.render_molecule(), width=600)
        handle_add_to_favourites(index)

    st.subheader("Synthesis")
    # Render the reaction scheme
    total_steps = len(molecule.pathway)
    for i, step in enumerate(molecule.pathway):
        cont_step = st.container(border=True, horizontal_alignment="center")
        with cont_step:
            try:
                st.write(f"**Step {i+1}** of {total_steps}:")
                st.image(step.render_diagram(size=(1600, 400)), width="stretch")
            except Exception as e:
                # Handle errors -> send report
                st.error(f"Error rendering pathway: {e}")
                cont_er = st.container(border=True)
                with cont_er:
                    handle_pathway_rendering_error(dataset, index, e)
else:
    st.warning("Load a dataset to see this page", icon="⚠️")

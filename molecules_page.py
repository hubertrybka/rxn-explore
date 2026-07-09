import streamlit as st
import datetime
from src.utils import calculate_descriptors
import yaml

st.header("Browse Molecules")

if st.session_state['dataset'] is not None:

    # Select a molecule from the dataset by index
    dataset = st.session_state['dataset']

    # Display the molecule
    left_col, right_col = st.columns([1, 1])
    with left_col:
        st.write("**Select index of the molecule you want to display**")
        st.caption("(molecules are indexed from 0)")
        index = st.number_input("Index:",
                                min_value=0,
                                max_value=dataset.n_molecules - 1,
                                value=st.session_state['view_index'],
                                step=1,
                                width=200)
        molecule = dataset[index]

        # Display calculated properties
        descriptors = calculate_descriptors(molecule.get_smiles())
        st.subheader("Calculated properties")
        st.dataframe(descriptors, width='content', hide_index=True)

    with right_col:
        con_1 = st.container(border=True, width='content')
        with con_1:
            st.image(molecule.render_molecule(), width=600)
            button_color = "primary" if index in st.session_state['favourite_idcs'] else "secondary"
            fav = st.button("Favourite", icon="⭐", type=button_color)
            if fav:
                if index not in st.session_state['favourite_idcs']:
                    st.session_state['favourite_idcs'].append(index)
                    st.rerun()

    con_2 = st.container(border=True)
    with con_2:
        # Display the pathway
        st.subheader("Pathway")
        try:
            # Render the pathway
            for i, step in enumerate(molecule.pathway):
                st.write(f"* Step {i+1}:")
                st.image(step.render_diagram(), width='stretch')
        except Exception as e:
            # Handle errors -> send report
            st.error(f"Error rendering pathway: {e}")
            cont_error_pathway = st.container(border=True)
            with cont_error_pathway:
                st.write(f"**Pathway could not be rendered.** Let me know by sending a report:")
                if st.button("Report", type="primary", disabled=st.session_state['is_bugged'][index]):
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    molecule_raw = dataset.raw_data.iloc[index]
                    filename = f"bug_report_{timestamp}.txt"
                    with open(st.session_state['user_report_dir'] / filename, 'a') as f:
                        f.write(f"# Exception: {e}\n\n")
                        yaml = yaml.dump(molecule_raw.to_dict(), default_flow_style=False, width=50, indent=4)
                        f.write(yaml)
                    st.session_state['is_bugged'][index] = True
                    st.rerun()
else:
    st.warning("Load a dataset to browse this page")

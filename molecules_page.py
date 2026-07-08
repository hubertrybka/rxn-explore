import streamlit as st

st.title("Browse Molecules")

if st.session_state['dataset'] is not None:
    # Select a molecule from the dataset by index
    dataset = st.session_state['dataset']
    index = st.number_input("Select molecule index",
                            min_value=0,
                            max_value=dataset.n_molecules-1,
                            value=0,
                            step=1)
    molecule = dataset[index]

    con_1 = st.container(border=True)
    with con_1:
        # Display the molecule
        st.image(molecule.render_molecule(), width=400)
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
        for step in molecule.pathway:
            st.image(step.render_diagram())
else:
    st.warning("Load a dataset to browse this page")
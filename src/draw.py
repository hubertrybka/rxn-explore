from io import BytesIO
from typing import Tuple

import streamlit as st
from PIL import Image
from rdkit import Chem
from rdkit.Chem import Draw, rdChemReactions, rdDepictor


@st.cache_data(show_spinner=False)
def draw_mol_from_smiles(
    smiles: str, size: Tuple[int, int] = (600, 600), bondwidth=4, fontsize=0.6
) -> Image.Image:
    mol = Chem.MolFromSmiles(smiles)
    rdDepictor.Compute2DCoords(mol)
    rdDepictor.StraightenDepiction(mol)

    d2d = Draw.MolDraw2DCairo(size[0], size[1])
    opts = d2d.drawOptions()
    opts.bondLineWidth = bondwidth
    opts.clearBackground = True
    opts.baseFontSize = fontsize

    d2d.DrawMolecule(mol)
    d2d.FinishDrawing()
    bio = BytesIO(d2d.GetDrawingText())
    return Image.open(bio)


@st.cache_data(
    show_spinner=False,
    hash_funcs={
        Chem.Mol: lambda mol: Chem.MolToSmiles(mol) if mol is not None else "",
        rdChemReactions.ChemicalReaction: rdChemReactions.ReactionToSmarts,
    },
)
def draw_highlighted_reaction(
    reacts,
    prods,
    includeAtomMaps=False,
    highlightAllAtoms=True,
    mapAllAtoms=False,
    highlightColors=None,
    size=(1200, 400),
    annotationFontScale=0.74,
) -> Image.Image:
    """
    Adapted from Greg Landrum (2025)
    draws a specific reaction with the reactants and products highlighted
    Returns an Image object with the drawing.
    """

    # make copies of all the reactants and the products since we will modify them
    reacts = [Chem.Mol(r) for r in reacts]
    prods = [Chem.Mol(p) for p in prods]

    # find the largest atom map number, used to initialize the negative atom map numbers
    #  when we are doing highlightAllAtoms
    negVal = 0
    if mapAllAtoms:
        for prod in prods:
            for at in prod.GetAtoms():
                if at.HasProp("old_mapno"):
                    negVal = min(negVal, -1 * at.GetIntProp("old_mapno"))
    negVal -= 1

    # loop over each of the products and set the atom map and note information
    #  in both the product atoms and corresponding reactant atoms.
    for prod in prods:
        for at in prod.GetAtoms():
            pd = at.GetPropsAsDict()
            mno = pd.get("old_mapno", negVal)
            if mno < 0:
                if not highlightAllAtoms:
                    continue
                else:
                    negVal -= 1

            r = reacts[pd["react_idx"]]
            rat = r.GetAtomWithIdx(pd["react_atom_idx"])
            for tat in at, rat:
                tat.SetAtomMapNum(mno)
                if includeAtomMaps and (mno > 0 or mapAllAtoms):
                    tat.SetProp("atomNote", str(mno))

    # create the reaction we'll actually render:
    nrxn = rdChemReactions.ChemicalReaction()
    for react in reacts:
        nrxn.AddReactantTemplate(react)
    for prod in prods:
        nrxn.AddProductTemplate(prod)

    # and draw it
    d2d = Draw.MolDraw2DCairo(size[0], size[1])
    opts = d2d.drawOptions()
    opts.annotationFontScale = 0
    opts.bondLineWidth = 2
    opts.clearBackground = True
    d2d.DrawReaction(
        nrxn, highlightByReactant=True, highlightColorsReactants=highlightColors
    )
    d2d.FinishDrawing()
    bio = BytesIO(d2d.GetDrawingText())
    return Image.open(bio)

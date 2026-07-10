import ast
import pathlib
from typing import Any, List, Tuple

import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, Mol

from src.draw import draw_highlighted_reaction, draw_mol_from_smiles


class Step:
    def __init__(self, reaction: str, reactants: Mol | Tuple[Mol, Mol], product: Mol):
        self.reaction = reaction
        self.reactants = reactants
        self.rxn = AllChem.ReactionFromSmarts(reaction)
        self.product = product

    def get_product(self) -> Mol:
        return self.rxn.RunReactants(self.reactants)[0]

    def render_diagram(self, size=(1200, 400)):
        return draw_highlighted_reaction(self.reactants, self.get_product(), size=size)


class MoleculeData:
    def __init__(self, df):
        self.df = df

        self.smiles_col_name = "molecule"
        self.synthesis_col_name = "path"

        self.pathway = self._make_pathway()

    def get_smiles(self):
        return self.df[self.smiles_col_name]

    def _make_pathway(self) -> List[Step]:
        path_string = self.df[self.synthesis_col_name]
        path_list = ast.literal_eval(path_string)
        no_steps = int((len(path_list) - 1) / 2)
        steps = []
        for i in range(no_steps):
            substrate = path_list[2 * i]
            reaction, reagent = path_list[2 * i + 1]
            product = Chem.MolFromSmiles(path_list[2 * i + 2])
            if reagent is None:
                reactants = Chem.MolFromSmiles(substrate)
            else:
                reactants = (Chem.MolFromSmiles(substrate), Chem.MolFromSmiles(reagent))
            step = Step(reaction, reactants, product)
            steps.append(step)
        return steps

    def render_molecule(self, as_preview=False):
        if as_preview:
            return draw_mol_from_smiles(
                self.get_smiles(), (250, 250), bondwidth=2, fontsize=1
            )
        else:
            return draw_mol_from_smiles(self.get_smiles(), (600, 600))


class MoleculeDataset:

    def __init__(
        self,
        molecules: List[MoleculeData],
        data_dir: pathlib.Path,
        raw_data: pd.DataFrame | None = None,
    ):
        self.molecules = molecules
        self.data_dir = pathlib.Path(data_dir)
        self.raw_data = raw_data

    def __getitem__(self, index):
        if index < 0 or index >= len(self.molecules):
            raise IndexError("Molecule index out of range")
        return self.molecules[index]

    def load(self, path: Any, from_pkl=False):
        if from_pkl:
            self.raw_data = pd.read_pickle(path)
        else:
            self.raw_data = pd.read_csv(path)
        self.molecules = [MoleculeData(row) for _, row in self.raw_data.iterrows()]

    @property
    def n_molecules(self):
        return len(self.molecules)

    def save(self, filename: str):
        save_path = self.data_dir / (filename + ".pkl")
        if save_path.exists():
            raise Exception(
                f"File `{filename}` already exists in library. Choose a different name."
            )
        self.raw_data.to_pickle(save_path)

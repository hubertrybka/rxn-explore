from rdkit.Chem import AllChem
from rdkit import Chem
from src.draw import draw_highlighted_reaction, draw_mol_from_smiles
import ast
import datetime
from typing import List, Tuple
import pathlib
from rdkit.Chem import Mol
import pandas as pd
from typing import Any

class Step:
    def __init__(self, reaction: str, reactants: Mol | Tuple[Mol, Mol], product: Mol):
        self.reaction = reaction
        self.reactants = reactants
        self.rxn = AllChem.ReactionFromSmarts(reaction)
        self.product = product

    def get_reaction(self):
        return self.reaction

    def get_reactants(self):
        return self.reactants

    def get_product(self) -> Mol:
        return self.rxn.RunReactants(self.reactants)[0]

    def render_diagram(self):
        return draw_highlighted_reaction(self.rxn, self.reactants, self.get_product())

class MoleculeData:
    def __init__(self, df):
        self.df = df
        self.pathway = self._make_pathway()

    def get_smiles(self):
        return self.df['molecule']

    def get_step(self, index):
        if index < 0 or index >= len(self.pathway):
            raise IndexError("Step index out of range")
        return self.pathway[index]

    @property
    def n_reactions(self):
        return len(self.pathway)

    def _make_pathway(self) -> List[Step]:
        path_string = self.df['path']
        path_list = ast.literal_eval(path_string)
        no_steps = int((len(path_list)-1)/2)
        steps = []
        for i in range(no_steps):
            substrate = path_list[2*i]
            reaction, reagent = path_list[2*i+1]
            product = Chem.MolFromSmiles(path_list[2*i+2])
            if reagent is None:
                reactants = (Chem.MolFromSmiles(substrate))
            else:
                reactants = (Chem.MolFromSmiles(substrate), Chem.MolFromSmiles(reagent))
            step = Step(reaction, reactants, product)
            steps.append(step)
        return steps

    def render_molecule(self):
        return draw_mol_from_smiles(self.get_smiles())

class MoleculeDataset:

    def __init__(self, molecules: List[MoleculeData],
                 data_dir: pathlib.Path,
                 raw_data: pd.DataFrame | None = None):
        self.molecules = molecules
        self.data_dir = pathlib.Path(data_dir)
        self.creation_date = None
        self.raw_data = raw_data

    def __getitem__(self, index):
        if index < 0 or index >= len(self.molecules):
            raise IndexError("Molecule index out of range")
        return self.molecules[index]

    def load(self, path: pathlib.Path | Any, from_pkl=False):
            if from_pkl:
                self.raw_data = pd.read_pickle(path)
            else:
                self.raw_data = pd.read_csv(path)
            molecules = []
            for n, row in self.raw_data.iterrows():
                molecule_data = MoleculeData(row)
                molecules.append(molecule_data)
            self.molecules = molecules

    @property
    def n_molecules(self):
        return len(self.molecules)

    def log_datetime(self):
        self.creation_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def save(self, filename: str):
        self.log_datetime()
        save_path = self.data_dir / (filename + '.pkl')
        if save_path.exists():
            raise Exception(f"File {filename} already exists. Please choose a different name.")
        self.raw_data.to_pickle(save_path)
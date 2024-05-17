import os
import os.path as osp
import pandas as pd
import torch

from typing import Callable, List, Optional
from torch_geometric.data import Data, download_url, extract_zip, InMemoryDataset
from torch_geometric.utils import one_hot
from rdkit import Chem, RDLogger
from rdkit.Chem.rdchem import HybridizationType
RDLogger.DisableLog('rdApp.*')


TYPES = {
    'H': 0, 'C': 1, 'N': 2, 'O': 3,
    'F': 4, 'Si': 5, 'P': 6, 'S': 7,
    'Cl': 8, 'Br': 9, 'I': 10,
    'Na': 11, 'Ge': 12
}

class Polymers(InMemoryDataset):

    raw_url = 'https://www.dropbox.com/scl/fi/ykbeg4u7fzlobua4m9tju/datasets.zip?rlkey=dsnmkmq6pdt4tvkrp6wktj9cj&st=5ad79o02&dl=1'

    def __init__(self, root: str, task_id: int, transform: Optional[Callable] = None,
                 pre_transform: Optional[Callable] = None,
                 pre_filter: Optional[Callable] = None):
        self.task_id = task_id
        super().__init__(root, transform, pre_transform, pre_filter)
        self.data, self.slices = torch.load(self.processed_paths[0])

    @property
    def raw_file_names(self) -> List[str]:
        return ['polymers.csv']

    @property
    def processed_file_names(self) -> str:
        return 'data.pt'

    def download(self):

        file_path = download_url(self.raw_url, self.raw_dir)
        extract_zip(file_path, self.raw_dir)
        os.unlink(file_path)

        for file in os.listdir(self.raw_dir):
            file_path = os.path.join(self.raw_dir, file)
            if file != 'dataset_{}.csv'.format(self.task_id):
                os.remove(file_path)

        os.rename(osp.join(self.raw_dir, 'dataset_{}.csv'.format(self.task_id)),
                  osp.join(self.raw_dir, 'polymers.csv'))

    def get_features(self, mol, target, features):

        N = mol.GetNumAtoms()

        type_idx = []
        atomic_number = []
        aromatic = []
        sp = []
        sp2 = []
        sp3 = []
        num_hs = []
        pp = []
        ratio = []
        monid = []

        for atom in mol.GetAtoms(): # for each atom
            type_idx.append(TYPES[atom.GetSymbol()])
            atomic_number.append(atom.GetAtomicNum())
            aromatic.append(1 if atom.GetIsAromatic() else 0)
            hybridization = atom.GetHybridization()
            sp.append(1 if hybridization == HybridizationType.SP else 0)
            sp2.append(1 if hybridization == HybridizationType.SP2 else 0)
            sp3.append(1 if hybridization == HybridizationType.SP3 else 0)
            num_hs.append(atom.GetNumExplicitHs())
            pp.append(atom.GetIntProp('polymerization_point'))
            ratio.append(atom.GetDoubleProp('ratio'))
            monid.append(atom.GetIntProp('monomer_id'))

        z = torch.tensor(atomic_number, dtype=torch.long)

        row, col = [], []
        for bond in mol.GetBonds():
            start, end = bond.GetBeginAtomIdx(), bond.GetEndAtomIdx()
            row += [start, end]
            col += [end, start]
        edge_index = torch.tensor([row, col], dtype=torch.long)

        perm = (edge_index[0] * N + edge_index[1]).argsort()
        edge_index = edge_index[:, perm]

        x1 = one_hot(torch.tensor(type_idx), num_classes=len(TYPES))
        x2 = torch.tensor([atomic_number, aromatic, sp, sp2, sp3, num_hs, pp],
                          dtype=torch.float).t().contiguous()
        x = torch.cat([x1, x2], dim=-1)

        data_kwargs = {
            'x': x, 'z': z, 'edge_index': edge_index, 'y': torch.tensor(target, dtype=torch.float32),
            'monomer_id': torch.tensor(monid), 'ratio': torch.tensor(ratio)
        }
        if features is not None:
            data_kwargs['feats'] = torch.tensor([[features]], dtype=torch.float32)
        return Data(**data_kwargs)
    
    def build_monomer(self, smi, ratio, monomer_id):

        mol = Chem.MolFromSmiles(smi)
        mol = Chem.rdmolops.AddHs(mol)

        for atom in mol.GetAtoms():
            atom.SetIntProp(
                'polymerization_point',
                int('*' in [a_n.GetSymbol() for a_n in atom.GetNeighbors()])
            )
            atom.SetDoubleProp('ratio', ratio)
            atom.SetIntProp('monomer_id', monomer_id)
        return Chem.DeleteSubstructs(mol, Chem.MolFromSmiles('[*]')), monomer_id + 1

    def process(self):

        df = pd.read_csv(self.raw_paths[0])
        monomer_id = 0
        data_list = []
        NMR_monomers = [
            'PEGA', 'HEA', 'TFEA', 
            'MSEA', 'HexaFOEA', 'NonaFOEA'
        ]
        acids = [
            '%SA', '%ADP', '%DDDA', '%AZL', 
            '%1,4-CHDA', '%1,3-CHDA', '%1,2-CHDA', '%HHPA', 
            '%PA', '%IPA', '%TPA', '%TMA'
        ]
        glycols = [
            '%EG', '%DEG', '%1,3-PROP', '%1,4-BUT', 
            '%HDO', '%NPG', '%1,4-CHDM', '%1,3-CHDM',
            '%TMCD', '%TMP', '%MPD', '%TCDDM'
        ]

        # task_id above 34 is classified as experimental dataset
        for i, (_, row) in enumerate(df.iterrows()):

            if self.task_id < 2:
                mol1, monomer_id = self.build_monomer(row['monoA'], row['%monoA'], monomer_id)
                mol2, monomer_id = self.build_monomer(row['monoB'], 1 - row['%monoA'], monomer_id)
                mol = Chem.CombineMols(mol1, mol2)
                features = None

            elif (self.task_id >= 2 and self.task_id <= 34) or self.task_id >= 38:
                mol, monomer_id = self.build_monomer(row['SMILES'], 1., monomer_id)
                if self.task_id == 13:
                    features = row['Slope']
                elif self.task_id == 23:
                    features = row['length']
                else:
                    features = None

            elif self.task_id == 37:
                # SNR dataset
                mols = []
                for monomer in NMR_monomers:
                    if row['%{}'.format(monomer)] > 0:
                        aux, monomer_id = self.build_monomer(row[monomer], row['%{}'.format(monomer)], monomer_id)
                        mols.append(aux)

                mol = mols[0] 
                for aux in mols[1:]: 
                    mol = Chem.CombineMols(mol, aux)
                features = row['Weight % Fluorine']
            
            elif self.task_id in [35, 36]:

                mols = []                      
                for acid in acids:
                    if row[acid] > 0:
                        aux, monomer_id = self.build_monomer(row[acid[1:]], row[acid], monomer_id)
                        mols.append(aux)
                for glycol in glycols:
                    if row[glycol] > 0:
                        aux, monomer_id = self.build_monomer(row[glycol[1:]], row[glycol], monomer_id)
                        mols.append(aux)

                mol = mols[0] 
                for aux in mols[1:]: 
                    mol = Chem.CombineMols(mol, aux)
                
                features = row['Mw']
                
            data = self.get_features(mol, row[row.index[-1]], features)

            if self.pre_filter is not None and not self.pre_filter(data):
                continue
            if self.pre_transform is not None:
                data = self.pre_transform(data)

            data_list.append(data)

        torch.save(self.collate(data_list), self.processed_paths[0])

'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/16 15:27
@Author  : JunYU
@File    : rdkit
'''
from typing import Any

from langchain.tools import BaseTool
from rapidfuzz.distance.Levenshtein_py import similarity
from rdkit.Chem.Fingerprints.ClusterMols import message

from rdkit import Chem
from rdkit.Chem import rdMolDescriptors

from ..utils import *

class MolSimilarity(BaseTool):
    name = "MolSimilarity"
    description = "Input two molecule SMILES (seperated by '.'), calculate Tanimoto similarity between two molecules and return the result"

    def __init__(self):
        super().__init__()

    def _run(self, smiles_pair:str) -> str:
        smi_list = smiles_pair.split(',')
        if len(smi_list) != 2:
            return "Input error, please input two molecule SMILES"
        else:
            smiles1, smiles2 = smi_list

        similarity = tanimoto(smiles1, smiles2)

        if(isinstance(similarity, str)):
            return similarity

        sim_score = {
            0.9: "very similar",
            0.8: "similar",
            0.7: "somewhat similar",
            0: "not similar"
        }
        if similarity == 1:
            return "Error: Input Molecules Are Identical"
        else:
            val = sim_score[max(key for key in sim_score.keys() if key <= round(similarity, 1))]
            message = f"The Tanimoto similarity between {smiles1} and {smiles2} is {round(similarity, 4)},\
                        indicating that the two molecules are {val}."
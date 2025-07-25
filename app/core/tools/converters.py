'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/19 00:16
@Author  : JunYU
@File    : converters
'''
from langchain.tools import BaseTool

from ..tools.chemspace import ChemSpace
from ..tools.safety import ControlChemCheck
from ..utils import (
    is_multiple_smiles,
    is_smiles,
    pubchem_query2smiles,
    query2cas,
    smiles2name,
)


class Query2CAS(BaseTool):
    name = "Mol2CAS"
    description = "Input molecule (name or SMILES), returns CAS number."
    url_cid: str = None
    url_data: str = None
    ControlChemCheck = ControlChemCheck()

    def __init__(
        self,
    ):
        super().__init__()
        self.url_cid = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/{}/{}/cids/JSON"
        )
        self.url_data = (
            "https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON"
        )

    def _run(self, query: str) -> str:
        try:
            # if query is smiles
            smiles = None
            if is_smiles(query):
                smiles = query
            try:
                cas = query2cas(query, self.url_cid, self.url_data)
            except ValueError as e:
                return str(e)
            if smiles is None:
                try:
                    smiles = pubchem_query2smiles(cas)
                except ValueError as e:
                    return str(e)
            # check if mol is controlled
            msg = self.ControlChemCheck._run(smiles)
            if "high similarity" in msg or "appears" in msg:
                return f"CAS number {cas}found, but " + msg
            return cas
        except ValueError:
            return "CAS number not found"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        return self._run(query)

class Query2SMILES(BaseTool):
    name = "Name2SMILES"
    description = "Input a molecule name, returns SMILES."
    url: str = None
    chemspace_api_key: str = None
    ControlChemCheck = ControlChemCheck()

    def __init__(self, chemspace_api_key: str = None):
        super().__init__()
        self.chemspace_api_key = chemspace_api_key
        # 修复：正确设置 PubChem 查询 URL
        self.url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/IsomericSMILES/JSON"

    def _run(self, query: str) -> str:
        if is_smiles(query) and is_multiple_smiles(query):
            return "Multiple SMILES strings detected, input one molecule at a time."
        try:
            smi = pubchem_query2smiles(query)
        except Exception as e:
            if self.chemspace_api_key:
                try:
                    chemspace = ChemSpace(self.chemspace_api_key)
                    smi = chemspace.convert_mol_rep(query, "smiles")
                    smi = smi.split(":")[1]
                except Exception:
                    return str(e)
            else:
                return str(e)

        msg = "Note: " + self.ControlChemCheck._run(smi)
        if "high similarity" in msg or "appears" in msg:
            return f"CAS number {smi}found, but " + msg
        return smi

    async def _arun(self, query: str) -> str:
        return self._run(query)

class SMILES2Name(BaseTool):
    name = "SMILES2Name"
    description = "Input SMILES, returns molecule name."
    ControlChemCheck = ControlChemCheck()
    query2smiles = Query2SMILES()

    def __init__(self):
        super().__init__()

    def _run(self, query: str) -> str:
        """Use the tool."""
        try:
            if not is_smiles(query):
                try:
                    query = self.query2smiles.run(query)
                except:
                    raise ValueError("Invalid molecule input, no Pubchem entry")
            name = smiles2name(query)
            # check if mol is controlled
            msg = "Note: " + self.ControlChemCheck._run(query)
            if "high similarity" in msg or "appears" in msg:
                return f"Molecule name {name} found, but " + msg
            return name
        except Exception as e:
            return "Error: " + str(e)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        return self._run(query)

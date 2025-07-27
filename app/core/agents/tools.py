'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/16 15:27
@Author  : JunYU
@File    : tools
'''
import os

from langchain import agents
from langchain.base_language import BaseLanguageModel

from ..tools import *


def make_tools(llm: BaseLanguageModel, api_keys: dict = {}, local_rxn: bool=False, verbose=True, user_id: int = None, conversation_id: str = None):
    serp_api_key = api_keys.get("SERP_API_KEY") or os.getenv("SERP_API_KEY")
    rxn4chem_api_key = api_keys.get("RXN4CHEM_API_KEY") or os.getenv("RXN4CHEM_API_KEY")
    openai_api_key = api_keys.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    chemspace_api_key = api_keys.get("CHEMSPACE_API_KEY") or os.getenv(
        "CHEMSPACE_API_KEY"
    )
    semantic_scholar_api_key = api_keys.get("SEMANTIC_SCHOLAR_API_KEY") or os.getenv(
        "SEMANTIC_SCHOLAR_API_KEY"
    )

    # 在新版本的LangChain中，python_repl工具已经移动到了langchain_community.tools
    try:
        from langchain_community.tools import PythonREPLTool
        all_tools = [PythonREPLTool()]
    except ImportError:
        # 如果导入失败，尝试使用旧的方式
        try:
            all_tools = agents.load_tools(["python_repl"])
        except ValueError:
            # 如果都失败了，使用空的工具列表
            all_tools = []
    
    # 维基百科功能已集成到WebSearch工具中

    all_tools += [
        Query2SMILES(chemspace_api_key),
        Query2CAS(),
        SMILES2Name(),
        PatentCheck(),
        MolSimilarity(),
        SMILES2Weight(),
        FuncGroups(),
        ExplosiveCheck(),
        ControlChemCheck(),
        SimilarControlChemCheck(),
        SafetySummary(llm=llm),
        Scholar2ResultLLM(
            llm=llm,
            openai_api_key=openai_api_key,
            semantic_scholar_api_key=semantic_scholar_api_key
        ),
    ]
    if chemspace_api_key:
        all_tools += [GetMoleculePrice(chemspace_api_key)]
    if serp_api_key:
        all_tools += [WebSearch(serp_api_key=serp_api_key)]
    if (not local_rxn) and rxn4chem_api_key:
        all_tools += [
            RXNPredict(rxn4chem_api_key),
            RXNRetrosynthesis(rxn4chem_api_key, openai_api_key),
        ]
    elif local_rxn:
        all_tools += [
            RXNPredictLocal(),
            RXNRetrosynthesisLocal()
        ]
    
    return all_tools

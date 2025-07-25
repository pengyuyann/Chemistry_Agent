'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/16 11:05
@Author  : JunYU
@File    : utils
'''

# This file is tool function code, includes check, split......

import re
import os

import requests
from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem

def is_smiles(text):
    try:
        m = Chem.MolFromSmiles(text, sanitize=False)
        if m is None:
            return False
        return True
    except:
        return False

def is_multiple_smiles(text):
    if is_smiles(text):
        return "." in text
    return False

def split_smiles(text):
    return text.split(".")

def is_cas(text):
    pattern = r"^\d{2,7}-\d{2} -\d$"
    return re.match(pattern, text) is not None

def largest_mol(smiles):
    ss = smiles.split(".")
    ss.sort(key=lambda a: len(a))
    while not is_multiple_smiles(ss[-1]):
        rm = ss[-1]
        ss.remove(rm)
    return ss[-1]

def canonical_smiles(smiles):
    try:
        smi = Chem.MolFromSmiles(Chem.MolFromSmiles(smiles), canonical=True)
        return smi
    except Exception:
        return "Invalid SMILES string"

def tanimoto(s1, s2):
    """Calculate the tanimoto similarity between two smiles"""
    try:
        mol1 = Chem.MolFromSmiles(s1)
        mol2 = Chem.MolFromSmiles(s2)
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)
        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except (TypeError, ValueError, AttributeError):
        return "Error: Not a valid SMILES string"

import requests                      # HTTP 请求库
from urllib.parse import quote       # 用于 URL 编码

def pubchem_query2smiles(query: str) -> str:
    """
    通过 PubChem 名称查询 SMILES（多级回退：Iso → Canonical → 普通）
    """
    # ① 将化学名进行 URL 编码，避免空格、中文导致 404
    query = query.strip()
    encoded = quote(query)


    # ② 一次性向 PubChem 请求三个字段，减少网络往返
    url = (
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/"
        f"{encoded}/property/IsomericSMILES,CanonicalSMILES,SMILES/JSON"
    )
    print(f"🔍 请求：{url}")
    # 设置代理
    proxies = {
        'http': os.environ.get('http_proxy'),
        'https': os.environ.get('https_proxy')
    }

    # ③ 发送 GET 请求，捕获网络异常
    try:
        res = requests.get(url, proxies= proxies,timeout=10)  # 10 秒超时
        res.raise_for_status()               # HTTP 非 200 抛异常
        data = res.json()                    # 解析 JSON
    except Exception as e:
        raise ValueError(f"网络错误或 PubChem 不可达：{e}")

    # ④ 提取属性字典
    try:
        props = data["PropertyTable"]["Properties"][0]
    except (KeyError, IndexError):
        raise ValueError("PubChem 返回结构异常，未找到 Properties 节点")

    # ⑤ 按优先级依次返回字段
    for field in ("IsomericSMILES", "CanonicalSMILES", "SMILES"):
        if field in props and props[field]:
            print(props[field])
            return props[field]

    # ⑥ 如果三个字段都不存在，抛出明确错误
    raise ValueError("未能获取到任何 SMILES 字段，请检查化学名是否正确")

def query2cas(query: str, url_cid: str, url_data: str):
    try:
        mode = "name"
        if is_smiles(query):
            if is_multiple_smiles(query):
                raise ValueError(
                    "Multiple SMILES strings detected, input one molecule at a time."
                )
            mode = "smiles"
        
        # 常见化学品名称映射
        common_chemicals = {
            # 中文名称映射
            "阿司匹林": "aspirin",
            "乙酰水杨酸": "aspirin", 
            "苯": "benzene",
            "乙醇": "ethanol",
            "甲醇": "methanol",
            "丙酮": "acetone",
            "乙酸": "acetic acid",
            "硫酸": "sulfuric acid",
            "盐酸": "hydrochloric acid",
            "氢氧化钠": "sodium hydroxide",
            "氯化钠": "sodium chloride",
            "葡萄糖": "glucose",
            "蔗糖": "sucrose",
            "咖啡因": "caffeine",
            "尼古丁": "nicotine",
            "吗啡": "morphine",
            "可卡因": "cocaine",
            "海洛因": "heroin",
            "大麻": "cannabis",
            "冰毒": "methamphetamine",
            # 英文名称映射
            "aspirin": "aspirin",
            "benzene": "benzene",
            "ethanol": "ethanol",
            "methanol": "methanol",
            "acetone": "acetone",
            "acetic acid": "acetic acid",
            "sulfuric acid": "sulfuric acid",
            "hydrochloric acid": "hydrochloric acid",
            "sodium hydroxide": "sodium hydroxide",
            "sodium chloride": "sodium chloride",
            "glucose": "glucose",
            "sucrose": "sucrose",
            "caffeine": "caffeine",
            "nicotine": "nicotine",
            "morphine": "morphine",
            "cocaine": "cocaine",
            "heroin": "heroin",
            "cannabis": "cannabis",
            "methamphetamine": "methamphetamine",
        }
        
        # 检查是否有映射
        if query in common_chemicals:
            query = common_chemicals[query]
        
        # 设置代理
        proxies = {
            'http': os.environ.get('http_proxy'),
            'https': os.environ.get('https_proxy')
        }
        
        url_cid = url_cid.format(mode, query)
        cid_response = requests.get(url_cid, proxies=proxies, timeout=30)
        cid_response.raise_for_status()
        cid = cid_response.json()["IdentifierList"]["CID"][0]
        
        url_data = url_data.format(cid)
        data_response = requests.get(url_data, proxies=proxies, timeout=30)
        data_response.raise_for_status()
        data = data_response.json()
    except (requests.exceptions.RequestException, KeyError):
        raise ValueError("Invalid molecule input, no Pubchem entry")

    try:
        for section in data["Record"]["Section"]:
            if section.get("TOCHeading") == "Names and Identifiers":
                for subsection in section["Section"]:
                    if subsection.get("TOCHeading") == "Other Identifiers":
                        for subsubsection in subsection["Section"]:
                            if subsubsection.get("TOCHeading") == "CAS":
                                try:
                                    return subsubsection["Information"][0]["Value"][
                                        "StringWithMarkup"
                                    ][0]["String"]
                                except (KeyError, IndexError):
                                    continue
    except (KeyError, IndexError):
        raise ValueError("Invalid molecule input, no Pubchem entry")

    raise ValueError("CAS number not found")


def smiles2name(smi, single_name=True):
    """This function queries the given molecule smiles and returns a name record or iupac"""

    try:
        smi = Chem.MolToSmiles(Chem.MolFromSmiles(smi), canonical=True)
    except Exception:
        raise ValueError("Invalid SMILES string")
    # query the PubChem database
    # 设置代理
    proxies = {
        'http': os.environ.get('http_proxy'),
        'https': os.environ.get('https_proxy')
    }
    
    r = requests.get(
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/smiles/"
        + smi
        + "/synonyms/JSON",
        proxies=proxies,
        timeout=30
    )
    r.raise_for_status()
    # convert the response to a json object
    data = r.json()
    # return the SMILES string
    try:
        if single_name:
            index = 0
            names = data["InformationList"]["Information"][0]["Synonym"]
            while index < len(names) and is_cas(name := names[index]):
                index += 1
                if index >= len(names):
                    raise ValueError("No name found")
        else:
            name = data["InformationList"]["Information"][0]["Synonym"]
    except (KeyError, IndexError):
        raise ValueError("Unknown Molecule")
    return name

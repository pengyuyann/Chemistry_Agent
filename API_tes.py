# '''
# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2025/7/16 13:55
# @Author  : JunYU
# @File    : API_tes
# '''
# import os
# os.environ["http_proxy"] = "http://127.0.0.1:7897"
# os.environ["https_proxy"] = "http://127.0.0.1:7897"
#
# from openai import OpenAI
#
# client = OpenAI(api_key="sk-bd9bde5fe1864c1cb23dccfd6759815c", base_url="https://api.deepseek.com")
#
# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant"},
#         {"role": "user", "content": "Hello"},
#     ],
#     stream=False
# )
#
# print(response.choices[0].message.content)
import requests
from urllib.parse import quote

def pubchem_query2smiles(query: str) -> str:
    url_template = "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{}/property/IsomericSMILES,CanonicalSMILES,SMILES/JSON"
    url = url_template.format(quote(query))
    print(f"🔍 正在请求: {url}")

    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        props = data["PropertyTabl  e"]["Properties"][0]
        for field in ["IsomericSMILES", "CanonicalSMILES", "SMILES"]:
            if field in props:
                return props[field]
        raise ValueError("❌ SMILES 字段都不存在")
    except Exception as e:
        raise ValueError(f"❌ 查询失败: {str(e)}")


print(pubchem_query2smiles("benzene"))

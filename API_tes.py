'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/16 13:55
@Author  : JunYU
@File    : API_tes
'''
import os
os.environ["http_proxy"] = "http://127.0.0.1:7897"
os.environ["https_proxy"] = "http://127.0.0.1:7897"

from openai import OpenAI

client = OpenAI(api_key="sk-bd9bde5fe1864c1cb23dccfd6759815c", base_url="https://api.deepseek.com")

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ],
    stream=False
)

print(response.choices[0].message.content)
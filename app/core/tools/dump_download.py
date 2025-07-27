'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/27 17:05
@Author  : JunYU
@File    : dump_download
'''
from paperscraper import get_dumps
import os

os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"
import time
from paperscraper import get_dumps

def download_with_progress(name, func):
    print(f"开始下载 {name}...")
    start = time.time()
    func()  # 调用对应的下载函数
    end = time.time()
    duration = end - start
    print(f"{name} 下载完成 ✅，用时：{duration:.2f} 秒\n")

if __name__ == "__main__":
    download_with_progress("biorxiv", get_dumps.biorxiv)
    download_with_progress("medrxiv", get_dumps.medrxiv)
    download_with_progress("chemrxiv", get_dumps.chemrxiv)


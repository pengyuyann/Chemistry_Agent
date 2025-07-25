'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/19 00:18
@Author  : JunYU
@File    : search
'''
import os
import re

import langchain
import molbloom
import paperqa
import paperscraper
from langchain import SerpAPIWrapper
from langchain.base_language import BaseLanguageModel
from langchain.tools import BaseTool
from langchain.embeddings.openai import OpenAIEmbeddings
from pypdf.errors import PdfReadError

from ..utils import is_multiple_smiles, split_smiles


def paper_scraper(search: str, pdir: str = "query", semantic_scholar_api_key: str = None) -> dict:
    try:
        # Windows系统不支持signal.SIGALRM，使用简单的超时处理
        import platform
        if platform.system() == "Windows":
            # Windows系统使用简单的搜索，不设置超时
            try:
                result = paperscraper.search_papers(
                    search,
                    pdir=pdir,
                    semantic_scholar_api_key=semantic_scholar_api_key,
                )
                
                # 确保返回的是字典类型
                if not isinstance(result, dict):
                    print(f"Warning: paper_scraper returned non-dict result: {type(result)}")
                    return {"error": f"Invalid result type: {type(result)}"}
                
                return result
            except Exception as e:
                print(f"Error in paperscraper.search_papers: {e}")
                return {"error": f"Search failed: {str(e)}"}
        else:
            # Unix/Linux系统使用信号超时
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError("Search timeout")
            
            # 设置30秒超时
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(30)
            
            try:
                result = paperscraper.search_papers(
                    search,
                    pdir=pdir,
                    semantic_scholar_api_key=semantic_scholar_api_key,
                )
                signal.alarm(0)  # 取消超时
                
                # 确保返回的是字典类型
                if not isinstance(result, dict):
                    print(f"Warning: paper_scraper returned non-dict result: {type(result)}")
                    return {"error": f"Invalid result type: {type(result)}"}
                
                return result
            except TimeoutError:
                signal.alarm(0)  # 取消超时
                return {"timeout": "Search timed out after 30 seconds"}
    except KeyError:
        return {}
    except Exception as e:
        print(f"Error in paper_scraper: {e}")
        return {"error": f"Search failed: {str(e)}"}


def paper_search(llm, query, semantic_scholar_api_key=None):
    prompt = langchain.prompts.PromptTemplate(
        input_variables=["question"],
        template="""
        I would like to find scholarly papers to answer
        this question: {question}. Your response must be at
        most 10 words long.
        'A search query that would bring up papers that can answer
        this question would be: '""",
    )

    query_chain = langchain.chains.llm.LLMChain(llm=llm, prompt=prompt)
    if not os.path.isdir("./query"):  # todo: move to ckpt
        os.mkdir("query/")
    search = query_chain.run(query)
    print("\nSearch:", search)
    papers = paper_scraper(search, pdir=f"query/{re.sub(' ', '', search)}", semantic_scholar_api_key=semantic_scholar_api_key)
    return papers


def scholar2result_llm(llm, query, k=5, max_sources=2, openai_api_key=None, semantic_scholar_api_key=None):
    """Useful to answer questions that require
    technical knowledge. Ask a specific question."""
    try:
        papers = paper_search(llm, query, semantic_scholar_api_key=semantic_scholar_api_key)
        
        # 检查是否有错误或超时
        if len(papers) == 0:
            return "Not enough papers found"
        
        # 检查是否有错误信息
        for key, value in papers.items():
            if isinstance(value, dict) and ("error" in value or "timeout" in value):
                return f"Search failed: {value.get('error', value.get('timeout', 'Unknown error'))}"
        
        print(f"Found {len(papers)} papers to process")
        
    except Exception as e:
        print(f"Error in scholar2result_llm: {e}")
        return f"Search failed: {str(e)}"
    # 检查是否是DeepSeek模型，如果是则使用不同的API基础URL
    if hasattr(llm, 'model_name') and (llm.model_name.startswith('deepseek-chat') or llm.model_name.startswith('deepseek-reasoner')):
        embeddings = OpenAIEmbeddings(
            openai_api_key=openai_api_key,
            openai_api_base="https://api.deepseek.com/v1"
        )
    else:
        embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
    
    docs = paperqa.Docs(
        llm=llm,
        summary_llm=llm,
        embeddings=embeddings,
    )
    not_loaded = 0
    for path, data in papers.items():
        try:
            # 添加调试信息
            print(f"Processing paper: path={path}, data_type={type(data)}, data={data}")
            
            # 检查data的类型，如果是字符串则直接使用，如果是字典则获取citation
            if isinstance(data, dict):
                citation = data.get("citation", str(data))
            elif isinstance(data, str):
                citation = data
            else:
                citation = str(data)
            
            docs.add(path, citation)
        except (ValueError, FileNotFoundError, PdfReadError) as e:
            print(f"Error processing paper {path}: {e}")
            not_loaded += 1
        except Exception as e:
            print(f"Unexpected error processing paper {path}: {e}")
            not_loaded += 1

    if not_loaded > 0:
        print(f"\nFound {len(papers.items())} papers but couldn't load {not_loaded}.")
    else:
        print(f"\nFound {len(papers.items())} papers and loaded all of them.")

    try:
        # 使用线程来避免事件循环冲突
        import threading
        import queue
        
        result_queue = queue.Queue()
        
        def run_query():
            try:
                answer = docs.query(query, k=k, max_sources=max_sources)
                result_queue.put(("success", answer.formatted_answer))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        # 在新线程中运行查询
        thread = threading.Thread(target=run_query)
        thread.start()
        thread.join(timeout=60)  # 60秒超时
        
        if thread.is_alive():
            return "文献搜索超时，请稍后重试。"
        
        if result_queue.empty():
            return "文献搜索失败，请稍后重试。"
        
        status, result = result_queue.get()
        if status == "success":
            return result
        else:
            print(f"Error in docs query: {result}")
            return f"Error processing papers: {result}"
            
    except Exception as e:
        print(f"Error in docs query: {e}")
        return f"Error processing papers: {str(e)}"


class Scholar2ResultLLM(BaseTool):
    name = "LiteratureSearch"
    description = (
        "Useful to answer questions that require technical "
        "knowledge. Ask a specific question."
    )
    llm: BaseLanguageModel = None
    openai_api_key: str = None
    semantic_scholar_api_key: str = None


    def __init__(self, llm, openai_api_key, semantic_scholar_api_key):
        super().__init__()
        self.llm = llm
        # api keys
        self.openai_api_key = openai_api_key
        self.semantic_scholar_api_key = semantic_scholar_api_key

    def _run(self, query) -> str:
        try:
            return scholar2result_llm(
                self.llm,
                query,
                openai_api_key=self.openai_api_key,
                semantic_scholar_api_key=self.semantic_scholar_api_key
            )
        except Exception as e:
            print(f"Error in LiteratureSearch tool: {e}")
            return f"Literature search failed: {str(e)}"

    async def _arun(self, query) -> str:
        """Use the tool asynchronously."""
        try:
            return self._run(query)
        except Exception as e:
            print(f"Error in LiteratureSearch async tool: {e}")
            return f"Literature search failed: {str(e)}"


def web_search(keywords, search_engine="google"):
    try:
        return SerpAPIWrapper(
            serpapi_api_key=os.getenv("SERP_API_KEY"), search_engine=search_engine
        ).run(keywords)
    except:
        return "No results, try another search"


class WebSearch(BaseTool):
    name = "WebSearch"
    description = (
        "Input a specific question, returns an answer from web search. "
        "Do not mention any specific molecule names, but use more general features to formulate your questions."
    )
    serp_api_key: str = None

    def __init__(self, serp_api_key: str = None):
        super().__init__()
        self.serp_api_key = serp_api_key

    def _run(self, query: str) -> str:
        if not self.serp_api_key:
            return (
                "No SerpAPI key found. This tool may not be used without a SerpAPI key."
            )
        return web_search(query)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        return self._run(query)


class PatentCheck(BaseTool):
    name = "PatentCheck"
    description = "Input SMILES, returns if molecule is patented. You may also input several SMILES, separated by a period."

    def _run(self, smiles: str) -> str:
        """Checks if compound is patented. Give this tool only one SMILES string"""
        if is_multiple_smiles(smiles):
            smiles_list = split_smiles(smiles)
        else:
            smiles_list = [smiles]
        try:
            output_dict = {}
            for smi in smiles_list:
                r = molbloom.buy(smi, canonicalize=True, catalog="surechembl")
                if r:
                    output_dict[smi] = "Patented"
                else:
                    output_dict[smi] = "Novel"
            return str(output_dict)
        except:
            return "Invalid SMILES string"

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        return self._run(query)

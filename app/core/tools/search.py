'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/19 00:18
@Author  : JunYU
@File    : search
'''
import os
import re
import json
import sys
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

import langchain
import molbloom
import paperqa
import paperscraper
from langchain_community.utilities import SerpAPIWrapper
from langchain.base_language import BaseLanguageModel
from langchain.tools import BaseTool
from langchain_community.embeddings import OpenAIEmbeddings
from pypdf.errors import PdfReadError

# 修复相对导入问题
try:
    from ..utils import is_multiple_smiles, split_smiles
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    try:
        from app.core.utils import is_multiple_smiles, split_smiles
    except ImportError:
        # 如果绝对导入也失败，添加路径并导入
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        if parent_dir not in sys.path:
            sys.path.insert(0, parent_dir)
        try:
            from utils import is_multiple_smiles, split_smiles
        except ImportError:
            # 最后的回退方案：定义简单的替代函数
            def is_multiple_smiles(text):
                return "." in text if text else False
            
            def split_smiles(text):
                return text.split(".") if text else []


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
    name: str = "LiteratureSearch"
    description: str = (
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
        # 检查API密钥
        serp_api_key = os.getenv("SERP_API_KEY")
        if not serp_api_key:
            return "SERP_API_KEY not found. Please set the environment variable."
        
        # 设置代理
        proxies = {
            'http': os.environ.get('http_proxy'),
            'https': os.environ.get('https_proxy')
        }
        
        # 创建SerpAPIWrapper实例
        serp_wrapper = SerpAPIWrapper(
            serpapi_api_key=serp_api_key, 
            search_engine=search_engine
        )
        
        # 如果设置了代理，尝试配置SerpAPI使用代理
        if proxies.get('http') or proxies.get('https'):
            try:
                # 设置requests的代理（如果SerpAPI内部使用requests）
                import requests
                session = requests.Session()
                session.proxies.update(proxies)
                # 注意：SerpAPI可能不支持直接设置代理，这里只是尝试
            except Exception as e:
                print(f"Warning: Could not set proxy for SerpAPI: {e}")
        
        # 执行搜索
        result = serp_wrapper.run(keywords)
        
        # 检查结果
        if not result or result.strip() == "":
            return "No results found for the search query."
        
        return result
        
    except Exception as e:
        error_msg = str(e)
        if "API key" in error_msg.lower():
            return "Invalid or missing SERP_API_KEY. Please check your API key."
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "SerpAPI quota exceeded or rate limit reached."
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            return "Network connection error. Please check your internet connection and proxy settings."
        else:
            return f"Search failed: {error_msg}"


def wikipedia_search(query):
    """维基百科搜索功能"""
    try:
        from langchain_community.utilities import WikipediaAPIWrapper
        import wikipedia
        import requests
        
        # 设置代理
        proxies = {
            'http': os.environ.get('http_proxy'),
            'https': os.environ.get('https_proxy')
        }
        
        # 创建维基百科API包装器
        wiki_wrapper = WikipediaAPIWrapper()
        
        # 设置wikipedia库的代理
        if proxies.get('http') or proxies.get('https'):
            # 直接设置环境变量，让wikipedia库使用代理
            original_http_proxy = os.environ.get('http_proxy')
            original_https_proxy = os.environ.get('https_proxy')
            
            # 确保环境变量已设置
            if not original_http_proxy:
                os.environ['http_proxy'] = proxies['http']
            if not original_https_proxy:
                os.environ['https_proxy'] = proxies['https']
        
        # 执行搜索
        result = wiki_wrapper.run(query)
        return result
    except Exception as e:
        return f"维基百科搜索失败: {str(e)}"


@dataclass
class SearchResult:
    """搜索结果数据结构"""
    title: str
    content: str
    url: str = ""
    source: str = ""
    relevance_score: float = 0.0
    metadata: Dict = None

class WebSearchReranker:
    """WebSearch专用的重排序器"""
    
    def __init__(self, use_local_reranker: bool = False):
        self.use_local_reranker = use_local_reranker
        
        # 初始化本地重排序器（如果启用）
        if self.use_local_reranker:
            self._init_local_reranker()
    
    def _init_local_reranker(self):
        """初始化本地重排序器"""
        try:
            from sentence_transformers import CrossEncoder
            self.local_reranker = CrossEncoder('BAAI/bge-reranker-v2-m3')
        except ImportError:
            print("Warning: sentence-transformers not installed, falling back to keyword-based reranking")
            self.use_local_reranker = False
    
    def rerank_search_results(self, query: str, search_results: List[SearchResult], top_k: int = 5) -> List[SearchResult]:
        """
        对搜索结果进行重排序
        
        Args:
            query: 查询文本
            search_results: 搜索结果列表
            top_k: 返回结果数量
            
        Returns:
            重排序后的结果列表
        """
        if not search_results:
            return []
        
        if self.use_local_reranker:
            return self._local_rerank(query, search_results, top_k)
        else:
            return self._keyword_rerank(query, search_results, top_k)
    
    def _local_rerank(self, query: str, search_results: List[SearchResult], top_k: int) -> List[SearchResult]:
        """使用本地重排序器"""
        try:
            # 准备重排序数据
            pairs = []
            for result in search_results:
                # 组合标题和内容作为文档
                document_text = f"{result.title} {result.content}"
                pairs.append([query, document_text])
            
            # 执行重排序
            scores = self.local_reranker.predict(pairs)
            
            # 更新相关性分数
            for i, result in enumerate(search_results):
                result.relevance_score = float(scores[i])
            
            # 按相关性分数排序
            search_results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            return search_results[:top_k]
            
        except Exception as e:
            print(f"Local reranking failed: {e}")
            # 回退到关键词重排序
            return self._keyword_rerank(query, search_results, top_k)
    
    def _keyword_rerank(self, query: str, search_results: List[SearchResult], top_k: int) -> List[SearchResult]:
        """基于关键词的重排序"""
        query_words = set(query.lower().split())
        
        for result in search_results:
            # 计算关键词匹配分数
            title_words = set(result.title.lower().split())
            content_words = set(result.content.lower().split())
            
            # 标题匹配权重更高
            title_overlap = len(query_words.intersection(title_words))
            content_overlap = len(query_words.intersection(content_words))
            
            # 计算相关性分数
            title_score = title_overlap / max(len(query_words), 1) * 0.7
            content_score = content_overlap / max(len(query_words), 1) * 0.3
            
            # 化学相关关键词加权
            chemistry_keywords = ['chemical', 'molecule', 'compound', 'reaction', 'synthesis', 
                                'catalyst', 'polymer', 'organic', 'inorganic', 'biochemistry']
            chemistry_bonus = 0
            for keyword in chemistry_keywords:
                if keyword in result.title.lower() or keyword in result.content.lower():
                    chemistry_bonus += 0.1
            
            result.relevance_score = min(title_score + content_score + chemistry_bonus, 1.0)
        
        # 按相关性分数排序
        search_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return search_results[:top_k]

def parse_search_results(raw_result: str, source: str = "web") -> List[SearchResult]:
    """解析搜索结果"""
    results = []
    
    if source == "wikipedia":
        # 维基百科结果通常是一个长文本
        if raw_result and "维基百科搜索失败" not in raw_result:
            # 简单分段处理
            paragraphs = raw_result.split('\n\n')
            for i, paragraph in enumerate(paragraphs[:3]):  # 取前3段
                if paragraph.strip():
                    result = SearchResult(
                        title=f"Wikipedia Section {i+1}",
                        content=paragraph.strip(),
                        source="wikipedia",
                        relevance_score=0.8 - i * 0.1  # 前面的段落权重更高
                    )
                    results.append(result)
    else:
        # 网络搜索结果解析
        # 这里需要根据SerpAPI的返回格式进行解析
        # 简化处理：将整个结果作为一个文档
        if raw_result and "No results found" not in raw_result:
            # 尝试提取标题和内容
            lines = raw_result.split('\n')
            current_title = ""
            current_content = ""
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 简单的标题检测（通常较短且可能包含特殊字符）
                if len(line) < 100 and ('http' in line or line.isupper() or line.endswith(':')):
                    if current_title and current_content:
                        result = SearchResult(
                            title=current_title,
                            content=current_content,
                            source="web",
                            relevance_score=0.5
                        )
                        results.append(result)
                    current_title = line
                    current_content = ""
                else:
                    current_content += line + " "
            
            # 添加最后一个结果
            if current_title and current_content:
                result = SearchResult(
                    title=current_title,
                    content=current_content,
                    source="web",
                    relevance_score=0.5
                )
                results.append(result)
            
            # 如果解析失败，将整个结果作为一个文档
            if not results:
                result = SearchResult(
                    title="Web Search Result",
                    content=raw_result,
                    source="web",
                    relevance_score=0.5
                )
                results.append(result)
    
    return results

class WebSearch(BaseTool):
    name: str = "WebSearch"
    description: str = (
        "Input a specific question, returns an answer from web search or Wikipedia. "
        "For general knowledge questions, Wikipedia will be used. For specific or recent information, web search will be used. "
        "Uses reranking to improve result relevance and quality. "
        "Do not mention any specific molecule names, but use more general features to formulate your questions."
    )
    
    # 添加字段声明
    serp_api_key: Optional[str] = None
    use_reranker: bool = True
    use_local_reranker: bool = False
    max_results: int = 5
    reranker: Optional[object] = None

    def __init__(self, 
                 serp_api_key: str = None, 
                 use_reranker: bool = True,
                 use_local_reranker: bool = False,
                 max_results: int = 5):
        super().__init__()
        
        # 直接设置属性
        self.serp_api_key = serp_api_key
        self.use_reranker = use_reranker
        self.use_local_reranker = use_local_reranker
        self.max_results = max_results
        
        # 初始化重排序器
        if self.use_reranker:
            self.reranker = WebSearchReranker(use_local_reranker=self.use_local_reranker)

    def _run(self, query: str) -> str:
        # 判断是否适合使用维基百科
        wikipedia_keywords = [
            'what is', 'who is', 'definition', 'history', 'background', 
            'introduction', 'overview', 'concept', 'theory', 'method',
            'process', 'technique', 'principle', 'basics', 'fundamentals'
        ]
        
        query_lower = query.lower()
        use_wikipedia = any(keyword in query_lower for keyword in wikipedia_keywords)
        
        all_results = []
        
        # 维基百科搜索
        if use_wikipedia:
            wiki_result = wikipedia_search(query)
            if "维基百科搜索失败" not in wiki_result:
                wiki_results = parse_search_results(wiki_result, "wikipedia")
                all_results.extend(wiki_results)
        
        # 网络搜索
        if not self.serp_api_key:
            if not all_results:
                return "No SerpAPI key found. This tool may not be used without a SerpAPI key."
        else:
            web_result = web_search(query)
            if "No results found" not in web_result and "failed" not in web_result.lower():
                web_results = parse_search_results(web_result, "web")
                all_results.extend(web_results)
        
        # 如果没有结果
        if not all_results:
            return "No relevant results found for the query."
        
        # 使用重排序器提升结果质量
        if self.use_reranker and hasattr(self, 'reranker'):
            try:
                reranked_results = self.reranker.rerank_search_results(
                    query, all_results, self.max_results
                )
            except Exception as e:
                print(f"Reranking failed: {e}")
                reranked_results = all_results[:self.max_results]
        else:
            reranked_results = all_results[:self.max_results]
        
        # 格式化输出
        return self._format_results(reranked_results, query)
    
    def _format_results(self, results: List[SearchResult], query: str) -> str:
        """格式化搜索结果"""
        if not results:
            return "No relevant results found."
        
        formatted_parts = []
        
        # 添加搜索摘要
        formatted_parts.append(f"🔍 搜索查询: {query}")
        formatted_parts.append(f"📊 找到 {len(results)} 个相关结果 (已重排序)")
        formatted_parts.append("")
        
        for i, result in enumerate(results, 1):
            part = f"【结果 {i}】"
            if result.source:
                part += f" ({result.source.upper()})"
            if hasattr(result, 'relevance_score') and result.relevance_score > 0:
                part += f" [相关性: {result.relevance_score:.2f}]"
            
            part += f"\n标题: {result.title}"
            part += f"\n内容: {result.content[:500]}..."  # 限制内容长度
            
            if result.url:
                part += f"\n链接: {result.url}"
            
            formatted_parts.append(part)
            formatted_parts.append("")
        
        return "\n".join(formatted_parts)

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        return self._run(query)


class PatentCheck(BaseTool):
    name: str = "PatentCheck"
    description: str = "Input SMILES, returns if molecule is patented. You may also input several SMILES, separated by a period."

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

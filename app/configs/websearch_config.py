"""
WebSearch工具配置
"""

import os
from typing import Dict, Any

class WebSearchConfig:
    """WebSearch工具配置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 重排序配置
        "use_reranker": True,
        "use_local_reranker": False,
        "max_results": 5,
        "rerank_top_k": 5,
        
        # 搜索配置
        "enable_wikipedia": True,
        "enable_web_search": True,
        "search_timeout": 30,
        
        # 结果处理配置
        "max_content_length": 500,
        "min_relevance_score": 0.1,
        
        # 化学相关关键词权重
        "chemistry_keyword_bonus": 0.1,
        "chemistry_keywords": [
            'chemical', 'molecule', 'compound', 'reaction', 'synthesis',
            'catalyst', 'polymer', 'organic', 'inorganic', 'biochemistry',
            'pharmaceutical', 'drug', 'medicine', 'chemistry', 'formula'
        ],
        
        # 重排序权重
        "title_weight": 0.7,
        "content_weight": 0.3,
        "source_weights": {
            "wikipedia": 0.8,
            "web": 0.6
        }
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化配置"""
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)
        
        # 从环境变量加载配置
        self._load_from_env()
    
    def _load_from_env(self):
        """从环境变量加载配置"""
        env_mappings = {
            "WEBSEARCH_USE_RERANKER": "use_reranker",
            "WEBSEARCH_USE_LOCAL_RERANKER": "use_local_reranker",
            "WEBSEARCH_MAX_RESULTS": "max_results",
            "WEBSEARCH_RERANK_TOP_K": "rerank_top_k",
            "WEBSEARCH_ENABLE_WIKIPEDIA": "enable_wikipedia",
            "WEBSEARCH_ENABLE_WEB_SEARCH": "enable_web_search",
            "WEBSEARCH_TIMEOUT": "search_timeout",
            "WEBSEARCH_MAX_CONTENT_LENGTH": "max_content_length",
            "WEBSEARCH_MIN_RELEVANCE_SCORE": "min_relevance_score",
            "WEBSEARCH_CHEMISTRY_BONUS": "chemistry_keyword_bonus",
            "WEBSEARCH_TITLE_WEIGHT": "title_weight",
            "WEBSEARCH_CONTENT_WEIGHT": "content_weight",
        }
        
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 类型转换
                if config_key in ["use_reranker", "use_local_reranker", "enable_wikipedia", "enable_web_search"]:
                    self.config[config_key] = env_value.lower() in ["true", "1", "yes"]
                elif config_key in ["chemistry_keyword_bonus", "min_relevance_score", "title_weight", "content_weight"]:
                    self.config[config_key] = float(env_value)
                elif config_key in ["max_results", "rerank_top_k", "search_timeout", "max_content_length"]:
                    self.config[config_key] = int(env_value)
                else:
                    self.config[config_key] = env_value
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
    
    def update(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()

# 全局配置实例
websearch_config = WebSearchConfig()
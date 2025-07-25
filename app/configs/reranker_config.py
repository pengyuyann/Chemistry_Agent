'''
!/usr/bin/env python
-*- coding: utf-8 -*-
@Time    : 2025/7/20 11:00
@Author  : JunYU
@File    : reranker_config
'''

import os
from typing import Dict, Any

class RerankerConfig:
    """重排序器配置"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 重排序模型配置
        "rerank_model": "bge-reranker-v2-m3",
        "use_local_reranker": False,
        
        # 向量搜索配置
        "embedding_model": "text-embedding-ada-002",
        "similarity_threshold": 0.3,
        "max_candidates": 10,
        "top_k_results": 5,
        
        # 重排序权重配置
        "similarity_weight": 0.7,
        "keyword_weight": 0.3,
        "entity_bonus": 0.5,
        "topic_bonus": 0.3,
        
        # 上下文配置
        "max_context_length": 1000,
        "context_window_size": 6,
        "history_context_limit": 3,
        
        # 性能配置
        "enable_caching": True,
        "cache_ttl": 3600,  # 1小时
        "batch_size": 32,
        
        # API配置
        "timeout": 30,
        "retry_attempts": 3,
        "retry_delay": 1,
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
            "RERANK_MODEL": "rerank_model",
            "USE_LOCAL_RERANKER": "use_local_reranker",
            "EMBEDDING_MODEL": "embedding_model",
            "SIMILARITY_THRESHOLD": "similarity_threshold",
            "MAX_CANDIDATES": "max_candidates",
            "TOP_K_RESULTS": "top_k_results",
            "SIMILARITY_WEIGHT": "similarity_weight",
            "KEYWORD_WEIGHT": "keyword_weight",
            "ENTITY_BONUS": "entity_bonus",
            "TOPIC_BONUS": "topic_bonus",
            "MAX_CONTEXT_LENGTH": "max_context_length",
            "CONTEXT_WINDOW_SIZE": "context_window_size",
            "HISTORY_CONTEXT_LIMIT": "history_context_limit",
            "ENABLE_CACHING": "enable_caching",
            "CACHE_TTL": "cache_ttl",
            "BATCH_SIZE": "batch_size",
            "TIMEOUT": "timeout",
            "RETRY_ATTEMPTS": "retry_attempts",
            "RETRY_DELAY": "retry_delay",
        }
        
        for env_key, config_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                # 类型转换
                if config_key in ["use_local_reranker", "enable_caching"]:
                    self.config[config_key] = env_value.lower() in ["true", "1", "yes"]
                elif config_key in ["similarity_threshold", "similarity_weight", "keyword_weight", 
                                  "entity_bonus", "topic_bonus"]:
                    self.config[config_key] = float(env_value)
                elif config_key in ["max_candidates", "top_k_results", "max_context_length", 
                                  "context_window_size", "history_context_limit", "cache_ttl", 
                                  "batch_size", "timeout", "retry_attempts", "retry_delay"]:
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
reranker_config = RerankerConfig() 
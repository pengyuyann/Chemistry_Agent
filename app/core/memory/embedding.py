"""
Embedding模块 - 使用HuggingFace模型进行文本向量化
"""
import os
import json
import hashlib
import logging
from typing import List, Dict, Optional, Union
from functools import lru_cache
import numpy as np

try:
    import torch
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    torch = None
    SentenceTransformer = None

from app.configs.embedding_config import EmbeddingConfig

logger = logging.getLogger(__name__)

class EmbeddingModel:
    """Embedding模型类"""
    
    def __init__(self, config: Optional[EmbeddingConfig] = None):
        self.config = config or EmbeddingConfig()
        self.model = None
        self.device = None
        self._cache = {}
        self._initialize_model()
    
    def _initialize_model(self):
        """初始化模型"""
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            logger.warning("sentence-transformers not available, falling back to hash-based embeddings")
            return
        
        try:
            # 设置设备
            self.device = self.config.get_device()
            logger.info(f"Using device: {self.device}")
            
            # 检查CUDA可用性
            if self.device.startswith("cuda") and not torch.cuda.is_available():
                logger.warning("CUDA requested but not available, falling back to CPU")
                self.device = "cpu"
            
            # 加载模型
            logger.info(f"Loading embedding model: {self.config.model_name}")
            self.model = SentenceTransformer(
                self.config.model_name,
                cache_folder=self.config.model_cache_dir,
                device=self.device
            )
            
            # 设置模型参数
            if hasattr(self.model, 'max_seq_length'):
                self.model.max_seq_length = self.config.max_seq_length
            
            logger.info(f"Model loaded successfully on {self.device}")
            
            # 测试模型
            test_embedding = self.model.encode("test", show_progress_bar=False)
            logger.info(f"Model test successful, embedding dimension: {len(test_embedding)}")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding model: {e}")
            self.model = None
    
    def encode(self, texts: Union[str, List[str]], 
               batch_size: Optional[int] = None,
               show_progress_bar: Optional[bool] = None) -> Union[np.ndarray, List[List[float]]]:
        """编码文本为向量"""
        if isinstance(texts, str):
            texts = [texts]
            single_text = True
        else:
            single_text = False
        
        # 检查缓存
        if self.config.enable_cache:
            cached_results = []
            uncached_texts = []
            uncached_indices = []
            
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    cached_results.append((i, self._cache[cache_key]))
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            
            if not uncached_texts:
                # 所有文本都在缓存中
                results = [None] * len(texts)
                for i, embedding in cached_results:
                    results[i] = embedding
                return results[0] if single_text else results
        else:
            uncached_texts = texts
            uncached_indices = list(range(len(texts)))
            cached_results = []
        
        # 编码未缓存的文本
        if uncached_texts:
            if self.model is not None:
                try:
                    embeddings = self._encode_with_model(
                        uncached_texts, 
                        batch_size or self.config.batch_size,
                        show_progress_bar if show_progress_bar is not None else self.config.show_progress_bar
                    )
                except Exception as e:
                    logger.error(f"Model encoding failed: {e}, falling back to hash-based embeddings")
                    embeddings = [self._hash_embedding(text) for text in uncached_texts]
            else:
                # 回退到哈希方法
                embeddings = [self._hash_embedding(text) for text in uncached_texts]
            
            # 更新缓存
            if self.config.enable_cache:
                for text, embedding in zip(uncached_texts, embeddings):
                    cache_key = self._get_cache_key(text)
                    self._cache[cache_key] = embedding
                    
                    # 限制缓存大小
                    if len(self._cache) > self.config.cache_size:
                        # 删除最旧的条目
                        oldest_key = next(iter(self._cache))
                        del self._cache[oldest_key]
        else:
            embeddings = []
        
        # 合并缓存和新计算的结果
        if self.config.enable_cache and cached_results:
            results = [None] * len(texts)
            
            # 填入缓存的结果
            for i, embedding in cached_results:
                results[i] = embedding
            
            # 填入新计算的结果
            for i, embedding in zip(uncached_indices, embeddings):
                results[i] = embedding
        else:
            results = embeddings
        
        return results[0] if single_text else results
    
    def _encode_with_model(self, texts: List[str], batch_size: int, show_progress_bar: bool) -> List[np.ndarray]:
        """使用模型编码文本"""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress_bar,
            normalize_embeddings=self.config.normalize_embeddings,
            convert_to_numpy=True
        )
        
        # 确保返回列表格式
        if isinstance(embeddings, np.ndarray):
            if embeddings.ndim == 1:
                return [embeddings.tolist()]
            else:
                return [emb.tolist() for emb in embeddings]
        
        return embeddings
    
    def _hash_embedding(self, text: str) -> List[float]:
        """哈希方法生成向量（回退方案）"""
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # 将哈希转换为向量
        vector = []
        target_dim = self.config.embedding_dim
        
        for i in range(0, len(hash_hex), 2):
            if len(vector) >= target_dim:
                break
            hex_pair = hash_hex[i:i+2]
            vector.append(int(hex_pair, 16) / 255.0)
        
        # 如果向量长度不够，用0填充
        while len(vector) < target_dim:
            vector.append(0.0)
        
        return vector[:target_dim]
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(f"{self.config.model_name}:{text}".encode()).hexdigest()
    
    def get_embedding_dim(self) -> int:
        """获取向量维度"""
        return self.config.embedding_dim
    
    def similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """计算余弦相似度"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def get_model_info(self) -> Dict:
        """获取模型信息"""
        info = {
            "model_name": self.config.model_name,
            "embedding_dim": self.config.embedding_dim,
            "device": self.device,
            "model_available": self.model is not None,
            "cuda_available": torch.cuda.is_available() if torch is not None else False,
            "cache_enabled": self.config.enable_cache,
            "cache_size": len(self._cache) if self.config.enable_cache else 0
        }
        
        if torch is not None and torch.cuda.is_available():
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_current_device"] = torch.cuda.current_device()
            
        return info

# 全局embedding实例
embedding_model = EmbeddingModel()
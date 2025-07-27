"""
Embedding模型配置
"""
import os
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class EmbeddingConfig:
    """Embedding模型配置类"""
    
    # 模型配置
    model_name: str = "text-embedding-ada-002"  # 默认使用OpenAI模型
    model_cache_dir: str = "./models/embeddings"  # 模型缓存目录
    
    # 设备配置
    device: str = "auto"  # auto, cpu, cuda, cuda:0, cuda:1, etc.
    use_cuda: bool = True  # 是否使用CUDA
    
    # 向量配置
    embedding_dim: int = 1536  # all-MiniLM-L6-v2的维度
    max_seq_length: int = 512  # 最大序列长度
    normalize_embeddings: bool = True  # 是否标准化向量
    
    # 批处理配置
    batch_size: int = 32  # 批处理大小
    show_progress_bar: bool = False  # 是否显示进度条
    
    # 缓存配置
    enable_cache: bool = True  # 是否启用缓存
    cache_size: int = 10000  # 缓存大小
    
    # 性能配置
    num_threads: int = 4  # 线程数
    
    def __post_init__(self):
        """初始化后处理"""
        # 从环境变量覆盖配置
        self.model_name = os.getenv("EMBEDDING_MODEL_NAME", self.model_name)
        self.model_cache_dir = os.getenv("EMBEDDING_CACHE_DIR", self.model_cache_dir)
        self.device = os.getenv("EMBEDDING_DEVICE", self.device)
        self.use_cuda = os.getenv("EMBEDDING_USE_CUDA", str(self.use_cuda)).lower() == "true"
        self.batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", str(self.batch_size)))
        self.enable_cache = os.getenv("EMBEDDING_ENABLE_CACHE", str(self.enable_cache)).lower() == "true"
        
        # 创建缓存目录
        os.makedirs(self.model_cache_dir, exist_ok=True)
        
        # 根据模型名称设置embedding维度
        self._set_embedding_dim()
    
    def _set_embedding_dim(self):
        """根据模型名称设置embedding维度"""
        model_dims = {
            "text-embedding-ada-002": 1536, # 新增OpenAI模型
            "sentence-transformers/all-MiniLM-L6-v2": 384,
            "sentence-transformers/all-mpnet-base-v2": 768,
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2": 384,
            "sentence-transformers/distiluse-base-multilingual-cased": 512,
            "BAAI/bge-small-en-v1.5": 384,
            "BAAI/bge-base-en-v1.5": 768,
            "BAAI/bge-large-en-v1.5": 1024,
            "BAAI/bge-small-zh-v1.5": 512,
            "BAAI/bge-base-zh-v1.5": 768,
            "BAAI/bge-large-zh-v1.5": 1024,
        }
        
        if self.model_name in model_dims:
            self.embedding_dim = model_dims[self.model_name]
    
    def get_device(self) -> str:
        """获取设备"""
        if self.device == "auto":
            import torch
            if self.use_cuda and torch.cuda.is_available():
                return "cuda"
            else:
                return "cpu"
        return self.device
    
    @classmethod
    def get_recommended_models(cls) -> List[dict]:
        """获取推荐的模型列表"""
        return [
            {
                "name": "text-embedding-ada-002",
                "description": "OpenAI 高质量模型",
                "dim": 1536,
                "size": "N/A",
                "languages": ["en", "zh"]
            },
            {
                "name": "sentence-transformers/all-MiniLM-L6-v2",
                "description": "轻量级英文模型，速度快",
                "dim": 384,
                "size": "80MB",
                "languages": ["en"]
            },
            {
                "name": "sentence-transformers/all-mpnet-base-v2",
                "description": "高质量英文模型",
                "dim": 768,
                "size": "420MB",
                "languages": ["en"]
            },
            {
                "name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
                "description": "多语言轻量级模型",
                "dim": 384,
                "size": "420MB",
                "languages": ["多语言"]
            },
            {
                "name": "BAAI/bge-base-zh-v1.5",
                "description": "中文优化模型",
                "dim": 768,
                "size": "400MB",
                "languages": ["zh", "en"]
            },
            {
                "name": "BAAI/bge-large-zh-v1.5",
                "description": "高质量中文模型",
                "dim": 1024,
                "size": "1.3GB",
                "languages": ["zh", "en"]
            }
        ]

# 默认配置实例
embedding_config = EmbeddingConfig()
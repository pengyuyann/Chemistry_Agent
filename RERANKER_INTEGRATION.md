# Chemistry Agent Reranker 集成指南

## 概述

本指南介绍如何在Chemistry Agent项目中集成reranker（重排序器）来提升对话历史检索的质量和相关性。

## 功能特性

### 1. 智能重排序
- 使用先进的reranker模型对向量搜索结果进行重排序
- 支持本地reranker（BGE-Reranker）和API reranker
- 考虑关键词匹配、实体匹配、主题匹配等多维度相关性

### 2. 上下文感知
- 结合当前对话上下文进行重排序
- 提供个性化的历史对话检索
- 支持对话连贯性增强

### 3. 工具集成
- 提供专门的reranker搜索工具
- 支持上下文增强工具
- 可在对话过程中主动使用

## 架构设计

```
用户查询 → 向量搜索 → Reranker重排序 → 上下文增强 → 最终回答
    ↓           ↓           ↓              ↓           ↓
对话历史    候选结果    相关性评分    增强提示    个性化回答
```

## 核心组件

### 1. Reranker模块 (`app/core/memory/reranker.py`)
- `Reranker`类：核心重排序器
- `RerankResult`：重排序结果数据结构
- 支持本地和API两种重排序方式

### 2. 向量存储增强 (`app/core/memory/vector_store.py`)
- 集成reranker到向量搜索流程
- 提供增强的上下文检索功能
- 支持对话上下文感知的搜索

### 3. Reranker工具 (`app/core/tools/reranker_tool.py`)
- `RerankerSearchTool`：历史对话搜索工具
- `ContextEnhancementTool`：上下文增强工具
- 可在对话过程中主动调用

### 4. 配置管理 (`app/configs/reranker_config.py`)
- 集中管理reranker相关配置
- 支持环境变量配置
- 提供灵活的配置选项

## 安装和配置

### 1. 安装依赖

```bash
# 安装本地reranker（可选）
pip install sentence-transformers

# 安装其他依赖
pip install numpy pandas
```

### 2. 环境变量配置

```bash
# 重排序模型配置
RERANK_MODEL=bge-reranker-v2-m3
USE_LOCAL_RERANKER=false

# 向量搜索配置
EMBEDDING_MODEL=text-embedding-ada-002
SIMILARITY_THRESHOLD=0.3
MAX_CANDIDATES=10
TOP_K_RESULTS=5

# 重排序权重配置
SIMILARITY_WEIGHT=0.7
KEYWORD_WEIGHT=0.3
ENTITY_BONUS=0.5
TOPIC_BONUS=0.3

# 上下文配置
MAX_CONTEXT_LENGTH=1000
CONTEXT_WINDOW_SIZE=6
HISTORY_CONTEXT_LIMIT=3
```

### 3. 启用reranker

在API调用时，reranker会自动启用。可以通过配置控制其行为：

```python
# 在ChemAgent初始化时
chemagent = ChemAgent(
    user_id=user_id,  # 启用用户特定的reranker工具
    conversation_id=conversation_id,
    # ... 其他参数
)
```

## 使用方法

### 1. 自动重排序

reranker会在每次对话时自动工作：

```python
# 在流式聊天API中
relevant_history = vector_store.get_relevant_context(
    db, current_user.id, request.input, conv_id, 
    top_k=3, conversation_context=conversation_context
)

# 使用增强的上下文提示
enhanced_prompt = chemagent.get_enhanced_context_prompt(
    request.input, conversation_context, relevant_history
)
```

### 2. 手动使用reranker工具

在对话过程中，ChemAgent可以使用reranker工具：

```python
# RerankerSearch工具
# 输入：搜索查询
# 输出：相关历史对话的详细信息

# ContextEnhancement工具
# 输入：当前对话内容
# 输出：增强的上下文信息
```

### 3. 配置调整

```python
from app.configs.reranker_config import reranker_config

# 调整重排序权重
reranker_config.set("similarity_weight", 0.8)
reranker_config.set("keyword_weight", 0.2)

# 调整搜索参数
reranker_config.set("max_candidates", 15)
reranker_config.set("top_k_results", 3)
```

## 性能优化

### 1. 缓存策略
- 启用向量缓存减少重复计算
- 配置合适的缓存TTL
- 使用批量处理提升效率

### 2. 模型选择
- 本地reranker：适合高隐私要求
- API reranker：适合快速部署
- 混合模式：根据需求动态选择

### 3. 参数调优
- 调整相似度阈值平衡精度和召回
- 优化重排序权重提升相关性
- 配置合适的候选数量

## 监控和调试

### 1. 日志记录
```python
# 在reranker中启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 性能监控
- 记录重排序耗时
- 监控相关性分数分布
- 跟踪缓存命中率

### 3. 质量评估
- 人工评估重排序结果
- 收集用户反馈
- 持续优化参数

## 最佳实践

### 1. 数据质量
- 确保对话历史的质量
- 定期清理无效数据
- 维护实体和主题的准确性

### 2. 用户体验
- 平衡相关性和多样性
- 避免过度依赖历史对话
- 提供透明的解释

### 3. 系统稳定性
- 实现优雅的降级机制
- 监控系统资源使用
- 定期备份重要数据

## 故障排除

### 1. 常见问题

**Q: 重排序结果不准确**
A: 检查相似度阈值和权重配置，调整参数

**Q: 性能较慢**
A: 启用缓存，减少候选数量，使用本地reranker

**Q: 内存使用过高**
A: 调整批处理大小，清理缓存，优化向量存储

### 2. 调试技巧
- 启用详细日志
- 使用小规模测试数据
- 逐步调整参数

## 未来扩展

### 1. 模型升级
- 支持更多reranker模型
- 集成多模态reranker
- 实现自适应模型选择

### 2. 功能增强
- 支持跨用户知识共享
- 实现动态权重调整
- 添加个性化推荐

### 3. 性能优化
- 实现分布式reranker
- 优化向量索引
- 支持实时更新

## 总结

通过集成reranker，Chemistry Agent能够提供更智能、更个性化的对话体验。重排序技术显著提升了历史对话检索的质量，使系统能够更好地理解用户意图并提供相关建议。

关键优势：
- 提升检索精度和相关性
- 增强对话连贯性
- 提供个性化体验
- 支持灵活的配置和扩展

建议在生产环境中逐步部署，持续监控和优化，以获得最佳效果。 
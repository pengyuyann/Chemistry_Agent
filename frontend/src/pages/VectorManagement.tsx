import React, { useState, useEffect } from 'react';
import { vectorApi, VectorStats, SearchTestResponse } from '../api/vector';
import './VectorManagement.css';

const VectorManagement: React.FC = () => {
  const [stats, setStats] = useState<VectorStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchTestResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await vectorApi.getStats();
      setStats(data);
    } catch (error) {
      setMessage('获取统计信息失败');
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (action: () => Promise<{ success: boolean; message: string }>) => {
    try {
      setLoading(true);
      setMessage('');
      const result = await action();
      setMessage(result.message);
      if (result.success) {
        await loadStats(); // 重新加载统计信息
      }
    } catch (error) {
      setMessage('操作失败');
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setSearchLoading(true);
      const result = await vectorApi.testSearch(searchQuery, 5);
      setSearchResults(result);
    } catch (error) {
      setMessage('搜索失败');
      console.error('Error searching:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const getStatusColor = (status: boolean) => status ? 'green' : 'red';
  const getStatusText = (status: boolean) => status ? '✅ 可用' : '❌ 不可用';

  return (
    <div className="vector-management">
      <h1>🔍 向量数据库管理</h1>
      
      {/* 统计信息 */}
      <div className="stats-section">
        <h2>📊 系统状态</h2>
        {loading ? (
          <div className="loading">加载中...</div>
        ) : stats ? (
          <div className="stats-grid">
            <div className="stat-card">
              <h3>FAISS 支持</h3>
              <p style={{ color: getStatusColor(stats.faiss_available) }}>
                {getStatusText(stats.faiss_available)}
              </p>
            </div>
            <div className="stat-card">
              <h3>Embedding 模型</h3>
              <p style={{ color: getStatusColor(stats.embeddings_available) }}>
                {getStatusText(stats.embeddings_available)}
              </p>
              <small>{stats.embedding_model}</small>
            </div>
            <div className="stat-card">
              <h3>向量数量</h3>
              <p>{stats.total_vectors || 0}</p>
            </div>
            <div className="stat-card">
              <h3>向量维度</h3>
              <p>{stats.dimension || 'N/A'}</p>
            </div>
          </div>
        ) : (
          <div className="error">无法加载统计信息</div>
        )}
      </div>

      {/* 操作按钮 */}
      <div className="actions-section">
        <h2>⚙️ 索引操作</h2>
        <div className="action-buttons">
          <button 
            onClick={() => handleAction(vectorApi.buildIndex)}
            disabled={loading}
            className="btn btn-primary"
          >
            🔨 构建索引
          </button>
          <button 
            onClick={() => handleAction(vectorApi.refreshIndex)}
            disabled={loading}
            className="btn btn-secondary"
          >
            🔄 刷新索引
          </button>
          <button 
            onClick={() => handleAction(vectorApi.batchUpdate)}
            disabled={loading}
            className="btn btn-info"
          >
            📦 批量更新
          </button>
          <button 
            onClick={() => handleAction(vectorApi.deleteIndex)}
            disabled={loading}
            className="btn btn-danger"
          >
            🗑️ 删除索引
          </button>
        </div>
      </div>

      {/* 搜索测试 */}
      <div className="search-section">
        <h2>🔍 搜索测试</h2>
        <div className="search-input">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="输入搜索查询..."
            className="search-field"
          />
          <button 
            onClick={handleSearch}
            disabled={searchLoading || !searchQuery.trim()}
            className="btn btn-primary"
          >
            {searchLoading ? '搜索中...' : '搜索'}
          </button>
        </div>
        
        {searchResults && (
          <div className="search-results">
            <h3>搜索结果: "{searchResults.query}"</h3>
            {searchResults.results.length > 0 ? (
              <div className="results-list">
                {searchResults.results.map((result, index) => (
                  <div key={index} className="result-item">
                    <div className="result-header">
                      <span className="conversation-id">对话: {result.conversation_id}</span>
                      <span className="similarity">相似度: {(result.similarity * 100).toFixed(2)}%</span>
                    </div>
                    <div className="result-details">
                      <div className="entities">
                        <strong>关键实体:</strong> {result.key_entities.join(', ') || '无'}
                      </div>
                      <div className="topics">
                        <strong>话题:</strong> {result.topics.join(', ') || '无'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p>没有找到相关结果</p>
            )}
          </div>
        )}
      </div>

      {/* 消息提示 */}
      {message && (
        <div className={`message ${message.includes('失败') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  );
};

export default VectorManagement; 
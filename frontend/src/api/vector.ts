import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 添加认证token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface VectorStats {
  use_faiss: boolean;
  embedding_model: string;
  embeddings_available: boolean;
  faiss_available: boolean;
  total_vectors?: number;
  dimension?: number;
  index_type?: string;
}

export interface SearchResult {
  conversation_id: string;
  similarity: number;
  key_entities: string[];
  topics: string[];
}

export interface SearchTestResponse {
  success: boolean;
  query: string;
  results: SearchResult[];
}

export const vectorApi = {
  // 获取向量数据库统计信息
  getStats: async (): Promise<VectorStats> => {
    const response = await api.get('/api/vector/stats');
    return response.data.data;
  },

  // 构建向量索引
  buildIndex: async (): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/api/vector/build');
    return response.data;
  },

  // 刷新向量索引
  refreshIndex: async (): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/api/vector/refresh');
    return response.data;
  },

  // 删除向量索引
  deleteIndex: async (): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete('/api/vector/index');
    return response.data;
  },

  // 批量更新向量
  batchUpdate: async (): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/api/vector/batch-update');
    return response.data;
  },

  // 测试向量搜索
  testSearch: async (query: string, topK: number = 5): Promise<SearchTestResponse> => {
    const response = await api.get(`/api/vector/test-search?query=${encodeURIComponent(query)}&top_k=${topK}`);
    return response.data;
  }
}; 
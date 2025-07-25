import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    console.log('API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.config.url);
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);

// API接口类型定义
export interface ChatRequest {
  input: string;
  conversation_id?: string;
  model?: string;
  tools_model?: string;
  temperature?: number;
  max_iterations?: number;
  streaming?: boolean;
  local_rxn?: boolean;
  api_keys?: Record<string, string>;
}

export interface ChatResponse {
  output: string;
  conversation_id: string;
  model_used: string;
  iterations?: number;
}

export interface ApiInfo {
  name: string;
  version: string;
  description: string;
  features: string[];
  supported_models: string[];
  endpoints: Record<string, string>;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
}

export interface ToolCategory {
  [key: string]: string[];
}

// API方法
export const apiService = {
  // 健康检查
  healthCheck: () => api.get<HealthStatus>('/health'),
  
  // 获取API信息
  getApiInfo: () => api.get<ApiInfo>('/api/info'),
  
  // ChemAgent健康检查
  getChemAgentHealth: () => api.get<HealthStatus>('/api/chemagent/health'),
  
  // 获取可用工具
  getAvailableTools: () => api.get<ToolCategory>('/api/chemagent/tools'),
  
  // 发送聊天消息
  sendChatMessage: (request: ChatRequest) => 
    api.post<ChatResponse>('/api/chemagent/', request),
};

// 新增流式聊天API
export function streamChatMessage(
  request: ChatRequest,
  onMessage: (text: string) => void,
  onEnd?: () => void,
  onError?: (err: any) => void
) {
  // 修正URL，去掉_chat
  const url = `${process.env.REACT_APP_API_URL || '/api'}/chemagent/stream_chat`;
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  }).then(response => {
    if (!response.body) throw new Error('No response body');
    const reader = response.body.getReader();
    let decoder = new TextDecoder('utf-8');
    let buffer = '';
    function read() {
      reader.read().then(({ done, value }) => {
        if (done) {
          onEnd && onEnd();
          return;
        }
        buffer += decoder.decode(value, { stream: true });
        let lines = buffer.split('\n\n');
        buffer = lines.pop() || '';
        for (let line of lines) {
          if (line.startsWith('data:')) {
            onMessage(line.replace(/^data:\s*/, ''));
          }
        }
        read();
      }).catch(onError);
    }
    read();
  }).catch(onError);
}

export default apiService; 
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

export interface PendingFeedback {
  feedback_id: string;
  type: string;
  task_description: string;
  risk_assessment: string;
  questions: string[];
  created_at: string;
}

export interface FeedbackHistory {
  feedback_id: string;
  type: string;
  task_description: string;
  risk_assessment: string;
  questions: string;
  status: string;
  response_message: string;
  expert_name: string;
  created_at: string;
  updated_at: string;
}

export interface FeedbackStats {
  status_distribution: Record<string, number>;
  type_distribution: Record<string, number>;
  recent_7_days: number;
  total: number;
}

export interface FeedbackActionRequest {
  expert_name: string;
  message: string;
}

export const feedbackApi = {
  // 获取待处理的反馈请求
  getPendingFeedbacks: async (): Promise<PendingFeedback[]> => {
    const response = await api.get('/api/feedback/pending');
    return response.data.data;
  },

  // 批准反馈请求
  approveFeedback: async (feedbackId: string, request: FeedbackActionRequest): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(`/api/feedback/${feedbackId}/approve`, request);
    return response.data;
  },

  // 拒绝反馈请求
  rejectFeedback: async (feedbackId: string, request: FeedbackActionRequest): Promise<{ success: boolean; message: string }> => {
    const response = await api.post(`/api/feedback/${feedbackId}/reject`, request);
    return response.data;
  },

  // 获取反馈历史记录
  getFeedbackHistory: async (limit: number = 50, offset: number = 0): Promise<{
    feedbacks: FeedbackHistory[];
    total: number;
    limit: number;
    offset: number;
  }> => {
    const response = await api.get(`/api/feedback/history?limit=${limit}&offset=${offset}`);
    return response.data.data;
  },

  // 获取反馈统计信息
  getFeedbackStats: async (): Promise<FeedbackStats> => {
    const response = await api.get('/api/feedback/stats');
    return response.data.data;
  },

  // 删除反馈记录
  deleteFeedback: async (feedbackId: string): Promise<{ success: boolean; message: string }> => {
    const response = await api.delete(`/api/feedback/${feedbackId}`);
    return response.data;
  }
}; 
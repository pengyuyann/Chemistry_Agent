import { api } from './api';

export interface UserProfile {
  user_id: number;
  username: string;
  email: string | null;
  is_admin: boolean;
  is_active: boolean;
  api_calls_count: number;
  api_calls_today: number;
  last_api_call: string | null;
  preferred_model: string;
  max_conversations: number;
  max_messages_per_conversation: number;
  last_login: string | null;
  created_at: string;
  updated_at: string;
  conversation_count: number;
  message_count: number;
}

export interface ApiUsage {
  api_calls_count: number;
  api_calls_today: number;
  last_api_call: string | null;
  usage_reset_date: string | null;
}

export interface UserPreferences {
  preferred_model: string;
  max_conversations: number;
  max_messages_per_conversation: number;
}

export async function login(username: string, password: string) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await api.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  
  return response.data;
}

export async function register(username: string, password: string, email?: string) {
  const response = await api.post('/auth/register', {
    username,
    password,
    email,
  });
  
  return response.data;
}

export async function getCurrentUser() {
  const response = await api.get('/auth/me');
  return response.data;
}

// 获取用户个人信息
export const getUserProfile = async (): Promise<UserProfile> => {
  const response = await api.get('/auth/profile');
  return response.data;
};

// 更新用户邮箱
export const updateUserEmail = async (email: string): Promise<{ message: string; email: string }> => {
  const response = await api.put('/auth/profile/email', { email });
  return response.data;
};

// 更新用户偏好设置
export const updateUserPreferences = async (preferences: Partial<UserPreferences>): Promise<{
  message: string;
  preferred_model: string;
  max_conversations: number;
  max_messages_per_conversation: number;
}> => {
  const response = await api.put('/auth/profile/preferences', preferences);
  return response.data;
};

// 获取API使用情况
export const getApiUsage = async (): Promise<ApiUsage> => {
  const response = await api.get('/auth/usage');
  return response.data;
}; 
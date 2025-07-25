import axios from 'axios';
import { getToken } from '../utils/token';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/auth';

export async function login(username: string, password: string) {
  const form = new FormData();
  form.append('username', username);
  form.append('password', password);
  const res = await fetch(`${API_BASE}/login`, {
    method: 'POST',
    body: form,
  });
  if (!res.ok) throw new Error('登录失败');
  return await res.json();
}

export async function register(username: string, password: string) {
  const res = await fetch(`${API_BASE}/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('注册失败');
  return await res.json();
}

export async function getMe() {
  const token = getToken();
  const res = await fetch(`${API_BASE}/me`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('获取用户信息失败');
  return await res.json();
} 
import { getToken } from '../utils/token';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/admin';

export async function getUsers() {
  const token = getToken();
  const res = await fetch(`${API_BASE}/users`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('获取用户列表失败');
  return await res.json();
}

export async function setAdmin(userId: number, isAdmin: boolean) {
  const token = getToken();
  const res = await fetch(`${API_BASE}/user/${userId}/set_admin?is_admin=${isAdmin}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('设置管理员失败');
  return await res.json();
}

export async function deleteUser(userId: number) {
  const token = getToken();
  const res = await fetch(`${API_BASE}/user/${userId}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('删除用户失败');
  return await res.json();
} 
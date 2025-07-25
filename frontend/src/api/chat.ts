import { getToken } from '../utils/token';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/chemagent';

// 添加认证头部的辅助函数
const getAuthHeaders = () => {
  const token = getToken();
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
};

export function streamChatMessage(
  request: any,
  onMessage: (text: string) => void,
  onEnd?: () => void,
  onError?: (err: any) => void
) {
  const url = `${API_BASE}/stream_chat`;
  console.log('[DEBUG] Making request to:', url);
  console.log('[DEBUG] Request body:', request);
  
  fetch(url, {
    method: 'POST',
    headers: { 
      ...getAuthHeaders(),
      'Accept': 'text/event-stream',
    },
    body: JSON.stringify(request),
  }).then(response => {
    console.log('[DEBUG] Response status:', response.status);
    console.log('[DEBUG] Response headers:', response.headers);
    if (!response.body) throw new Error('No response body');
    console.log('[DEBUG] Response body exists, starting to read stream');
    
    const reader = response.body.getReader();
    let decoder = new TextDecoder('utf-8');
    let buffer = '';
    let chunkCount = 0;
    
    function read() {
      reader.read().then(({ done, value }) => {
        chunkCount++;
        console.log(`[DEBUG] Read chunk ${chunkCount}, done: ${done}, value length: ${value?.length || 0}`);
        
        if (done) {
          console.log('[DEBUG] Stream finished');
          onEnd && onEnd();
          return;
        }
        
        const decoded = decoder.decode(value, { stream: true });
        console.log('[DEBUG] Decoded chunk:', decoded);
        buffer += decoded;
        
        // 按行分割，处理 SSE 格式
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // 保留不完整的行
        
        console.log('[DEBUG] Parsed lines:', lines);
        
        for (let line of lines) {
          line = line.trim();
          if (line.startsWith('data: ')) {
            const data = line.substring(6); // 移除 'data: ' 前缀
            console.log('[DEBUG] Received SSE data:', data);
            
            if (data.trim()) { // 确保不是空数据
              onMessage(data);
            }
          }
        }
        
        read();
      }).catch(error => {
        console.error('[DEBUG] Read error:', error);
        onError && onError(error);
      });
    }
    
    read();
  }).catch(error => {
    console.error('[DEBUG] Fetch error:', error);
    onError && onError(error);
  });
}

// 对话历史相关API
export async function getConversations(skip = 0, limit = 50) {
  const response = await fetch(`${API_BASE}/conversations?skip=${skip}&limit=${limit}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('获取对话历史失败');
  }
  
  return response.json();
}

export async function getConversation(conversationId: string) {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('获取对话详情失败');
  }
  
  return response.json();
}

export async function updateConversationTitle(conversationId: string, title: string) {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}/title`, {
    method: 'PUT',
    headers: getAuthHeaders(),
    body: JSON.stringify({ title }),
  });
  
  if (!response.ok) {
    throw new Error('更新对话标题失败');
  }
  
  return response.json();
}

export async function deleteConversation(conversationId: string) {
  const response = await fetch(`${API_BASE}/conversations/${conversationId}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('删除对话失败');
  }
  
  return response.json();
}

// 模型相关API
export async function getAvailableModels() {
  const response = await fetch(`${API_BASE}/models`, {
    method: 'GET',
    headers: getAuthHeaders(),
  });
  
  if (!response.ok) {
    throw new Error('获取模型列表失败');
  }
  
  return response.json();
} 
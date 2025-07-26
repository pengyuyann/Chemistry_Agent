import React, { useState, useRef, useEffect } from 'react';
import {
  message as antdMessage,
  Modal,
  Input as AntdInput,
} from 'antd';
import { 
  streamChatMessage, 
  getConversations, 
  getConversation, 
  updateConversationTitle, 
  deleteConversation,
  getAvailableModels 
} from '../api/chat';
import { useAuth } from '../context/AuthContext';
import ChatGPTStyleInterface from '../components/ChatGPTStyleInterface';
import { useNavigate } from 'react-router-dom';

interface ReasoningStep {
  thought: string;
  action: string;
  action_input: string;
  observation: string;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  model?: string;
  reasoningSteps?: ReasoningStep[];
  finalAnswer?: string;
  thinking?: string;
}

interface Conversation {
  id: string;
  title: string;
  model_used: string;
  created_at: string;
  updated_at: string;
  message_count: number;
}

interface Model {
  id: string;
  name: string;
  description: string;
}

const ChatInterface: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const typeWriterTimer = useRef<NodeJS.Timeout | null>(null);
  
  // 对话管理状态
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('deepseek-chat');
  const [availableModels, setAvailableModels] = useState<Model[]>([]);
  const [editTitleModal, setEditTitleModal] = useState(false);
  const [editingConversation, setEditingConversation] = useState<Conversation | null>(null);
  const [newTitle, setNewTitle] = useState('');
  const [loadingConversations, setLoadingConversations] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);
  const [deletingConversations, setDeletingConversations] = useState<Set<string>>(new Set());

  // 加载对话历史和可用模型
  useEffect(() => {
    loadConversations();
    loadAvailableModels();
  }, []);

  /**
   * 发送流式消息
   */
  const sendStreamMessage = async () => {
    if (!inputValue.trim()) return;
    setLoading(true);
    setStreaming(true);

    // 1️⃣ 插入 user 消息
    const userMsg: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');

    // 2️⃣ 插入占位 assistant 消息
    const assistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      type: 'assistant',
      content: '',
      timestamp: new Date(),
      model: 'deepseek-chat',
      reasoningSteps: [],
      finalAnswer: '',
    };
    setMessages(prev => [...prev, assistantMsg]);
    const lastMsgId = assistantMsg.id;

    // 清除旧的打字机 timer
    if (typeWriterTimer.current) clearTimeout(typeWriterTimer.current);

    /**
     * 调用后台 streamChatMessage
     */
    streamChatMessage(
      {
        input: userMsg.content,
        conversation_id: currentConversationId,
        model: selectedModel,
        tools_model: selectedModel,
        temperature: 0.1,
        max_iterations: 15,
        streaming: true,
        local_rxn: false,
        api_keys: {},
      },
      /** onMessage */
      (data: string) => {
        console.log('[DEBUG] Received data:', data);
        try {
          const obj = JSON.parse(data);
          console.log('[DEBUG] Parsed object:', obj);
          // 处理不同类型 chunk
          switch (obj.type) {
            case 'thinking':
              setMessages(prev => prev.map(m =>
                m.id === lastMsgId ? { ...m, thinking: obj.content } : m
              ));
              break;
            case 'thinking_end':
              setMessages(prev => prev.map(m =>
                m.id === lastMsgId ? { ...m, thinking: undefined } : m
              ));
              break;
            case 'tool_start':
              setMessages(prev => prev.map(m =>
                m.id === lastMsgId ? {
                  ...m,
                  reasoningSteps: [
                    ...(m.reasoningSteps || []),
                    {
                      thought: m.thinking || '',
                      action: obj.tool,
                      action_input: obj.input,
                      observation: '执行中…',
                    },
                  ],
                } : m
              ));
              break;
            case 'tool_end':
              setMessages(prev => prev.map(m => {
                if (m.id !== lastMsgId) return m;
                const steps = m.reasoningSteps || [];
                if (steps.length === 0) return m;
                // 更新最后一步 observation
                const updatedSteps = [...steps];
                updatedSteps[steps.length - 1] = {
                  ...updatedSteps[steps.length - 1],
                  observation: obj.output,
                };
                return { ...m, reasoningSteps: updatedSteps };
              }));
              break;
            case 'step':
              // ✅ 每接收一步立刻追加
              const newStep: ReasoningStep = {
                thought: obj.thought || '',
                action: obj.action || '',
                action_input: obj.action_input || '',
                observation: obj.observation || '',
              };
              setMessages(prev => prev.map(m =>
                m.id === lastMsgId
                  ? { ...m, reasoningSteps: [...(m.reasoningSteps || []), newStep] }
                  : m
              ));
              break;
            case 'final':
              // 打字机效果渲染 finalAnswer
              let i = 0;
              const txt: string = obj.output || '';
              const typeWriter = () => {
                if (i <= txt.length) {
                  setMessages(prev => prev.map(m =>
                    m.id === lastMsgId ? { ...m, finalAnswer: txt.slice(0, i) } : m
                  ));
                  i++;
                  typeWriterTimer.current = setTimeout(typeWriter, 16);
                }
              };
              typeWriter();
              break;
            case 'error':
              // 处理错误信息
              setMessages(prev => prev.map(m =>
                m.id === lastMsgId ? { ...m, finalAnswer: '❌ ' + (obj.message || '未知错误') } : m
              ));
              antdMessage.error(obj.message || '执行过程中出现错误');
              break;
            default:
              console.log('[DEBUG] Unknown message type:', obj.type);
              break;
          }
        } catch (e) {
          console.error('JSON parse error:', e);
        }
      },
      /** onDone */
      () => {
        setLoading(false);
        setStreaming(false);
        // 重新加载对话列表以更新最新对话
        loadConversations();
      },
      /** onError */
      (err: any) => {
        setLoading(false);
        setStreaming(false);
        setMessages(prev => prev.map(m =>
          m.id === lastMsgId
            ? { ...m, finalAnswer: '❌ 流式输出失败: ' + (err?.message || '未知错误') }
            : m
        ));
        antdMessage.error('流式输出失败');
      }
    );
  };

  // 清空对话
  const clearChat = () => {
    setMessages([]);
    antdMessage.info('对话已清空');
  };

  // 复制内容
  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    antdMessage.success('已复制到剪贴板');
  };

  // 加载对话历史
  const loadConversations = async () => {
    setLoadingConversations(true);
    try {
      const data = await getConversations();
      setConversations(data.conversations);
      
      // 如果有对话历史，自动加载最近的对话
      if (data.conversations.length > 0 && !currentConversationId) {
        const mostRecentConversation = data.conversations[0];
        await loadConversation(mostRecentConversation.id);
      }
    } catch (error) {
      antdMessage.error('加载对话历史失败');
      console.error('加载对话历史错误:', error);
    } finally {
      setLoadingConversations(false);
    }
  };

  // 加载可用模型
  const loadAvailableModels = async () => {
    setLoadingModels(true);
    try {
      const data = await getAvailableModels();
      setAvailableModels(data.models);
    } catch (error) {
      antdMessage.error('加载模型列表失败');
      console.error('加载模型列表错误:', error);
    } finally {
      setLoadingModels(false);
    }
  };

  // 加载特定对话
  const loadConversation = async (conversationId: string) => {
    try {
      const data = await getConversation(conversationId);
      setCurrentConversationId(conversationId);
      setSelectedModel(data.model_used);
      
      // 转换消息格式
      const convertedMessages: Message[] = data.messages.map((msg: any, index: number) => ({
        id: index.toString(),
        type: msg.role as 'user' | 'assistant',
        content: msg.content,
        timestamp: new Date(msg.created_at),
        model: msg.model_used,
        // 对于助手消息，将content设置为finalAnswer
        ...(msg.role === 'assistant' && { finalAnswer: msg.content }),
      }));
      
      setMessages(convertedMessages);
    } catch (error) {
      antdMessage.error('加载对话失败');
    }
  };

  // 创建新对话
  const createNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setInputValue('');
  };

  // 更新对话标题
  const handleUpdateTitle = async () => {
    if (!editingConversation || !newTitle.trim()) return;
    
    try {
      await updateConversationTitle(editingConversation.id, newTitle.trim());
      setEditTitleModal(false);
      setNewTitle('');
      setEditingConversation(null);
      loadConversations(); // 重新加载对话列表
      antdMessage.success('标题更新成功');
    } catch (error) {
      antdMessage.error('更新标题失败');
    }
  };

  // 删除对话
  const handleDeleteConversation = async (conversationId: string) => {
    // 防止重复删除
    if (deletingConversations.has(conversationId)) {
      return;
    }
    
    const conversation = conversations.find(c => c.id === conversationId);
    if (!conversation) return;
    
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除对话"${conversation.title}"吗？此操作不可恢复。`,
      okText: '删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        // 标记正在删除
        setDeletingConversations(prev => new Set(prev).add(conversationId));
        
        try {
          await deleteConversation(conversationId);
          if (currentConversationId === conversationId) {
            createNewConversation();
          }
          // 从本地状态中移除已删除的对话
          setConversations(prev => prev.filter(c => c.id !== conversationId));
          antdMessage.success('对话删除成功');
        } catch (error) {
          antdMessage.error('删除对话失败');
          console.error('删除对话错误:', error);
        } finally {
          // 移除删除标记
          setDeletingConversations(prev => {
            const newSet = new Set(prev);
            newSet.delete(conversationId);
            return newSet;
          });
        }
      }
    });
  };

  return (
    <>
      <ChatGPTStyleInterface
        messages={messages}
        inputValue={inputValue}
        setInputValue={setInputValue}
        onSendMessage={sendStreamMessage}
        loading={loading}
        streaming={streaming}
        copyMessage={copyMessage}
        clearChat={clearChat}
        selectedModel={selectedModel}
        availableModels={availableModels}
        onModelChange={setSelectedModel}
        conversations={conversations}
        currentConversationId={currentConversationId}
        onConversationSelect={loadConversation}
        onNewConversation={createNewConversation}
        onDeleteConversation={handleDeleteConversation}
        onEditConversationTitle={(conversation) => {
          setEditingConversation(conversation);
          setNewTitle(conversation.title);
          setEditTitleModal(true);
        }}
        loadingConversations={loadingConversations}
      />

      {/* 编辑标题模态框 */}
      <Modal
        title="编辑对话标题"
        open={editTitleModal}
        onOk={handleUpdateTitle}
        onCancel={() => {
          setEditTitleModal(false);
          setNewTitle('');
          setEditingConversation(null);
        }}
        okText="保存"
        cancelText="取消"
      >
        <AntdInput
          value={newTitle}
          onChange={(e) => setNewTitle(e.target.value)}
          placeholder="请输入新的对话标题"
          onPressEnter={handleUpdateTitle}
        />
      </Modal>
    </>
  );
};

export default ChatInterface;

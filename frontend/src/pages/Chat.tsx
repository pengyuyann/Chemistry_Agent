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
      
      // 后端直接返回数组，不是包含conversations字段的对象
      if (Array.isArray(data)) {
        setConversations(data);
        
        // 如果有对话历史，自动加载最近的对话
        if (data.length > 0 && !currentConversationId) {
          const mostRecentConversation = data[0];
          await loadConversation(mostRecentConversation.id);
        }
      } else {
        // 如果返回的数据格式不正确，设置为空数组
        console.warn('Invalid conversations data format:', data);
        setConversations([]);
      }
    } catch (error: any) {
      console.error('加载对话历史错误:', error);
      setConversations([]); // 设置为空数组避免后续错误
      
      // 如果是401错误，可能是认证问题
      if (error?.response?.status === 401) {
        antdMessage.error('认证失败，请重新登录');
      } else {
        antdMessage.error('加载对话历史失败');
      }
    } finally {
      setLoadingConversations(false);
    }
  };

  // 加载特定对话
  const loadConversation = async (conversationId: string) => {
    try {
      const data = await getConversation(conversationId);
      console.log('从后端获取的原始数据:', data); // 调试日志
      setCurrentConversationId(conversationId);
      
      // 检查data.messages是否存在
      if (data.messages && Array.isArray(data.messages)) {
        // 如果有消息，设置模型
        if (data.messages.length > 0) {
          const firstMessage = data.messages.find((msg: any) => msg.model_used);
          if (firstMessage) {
            setSelectedModel(firstMessage.model_used);
          }
        }
        
        // 转换消息格式
        const convertedMessages: Message[] = data.messages.map((msg: any, index: number) => {
          console.log(`消息 ${index} 的 steps:`, msg.steps); // 调试每条消息的steps
          return {
            id: index.toString(),
            type: msg.role as 'user' | 'assistant',
            content: msg.content,
            timestamp: new Date(msg.created_at),
            model: msg.model_used,
            // 处理思考步骤
            reasoningSteps: Array.isArray(msg.steps) ? msg.steps : [],
            // 对于助手消息，将content设置为finalAnswer
            ...(msg.role === 'assistant' && { finalAnswer: msg.content }),
          };
        });
        
        console.log('转换后的消息:', convertedMessages); // 调试转换后的数据
        setMessages(convertedMessages);
      } else {
        setMessages([]);
      }
    } catch (error: any) {
      console.error('加载对话失败:', error);
      antdMessage.error('加载对话失败');
      setMessages([]);
    }
  };

  // 创建新对话
  const createNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    antdMessage.info('已创建新对话');
  };

  // 加载可用模型
  const loadAvailableModels = async () => {
    setLoadingModels(true);
    try {
      const data = await getAvailableModels();
      setAvailableModels(data.models || []);
    } catch (error: any) {
      antdMessage.error('加载模型列表失败');
      console.error('加载模型列表错误:', error);
      setAvailableModels([]); // 设置默认值
    } finally {
      setLoadingModels(false);
    }
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
    } catch (error: any) {
      console.error('更新标题失败:', error);
      antdMessage.error('更新标题失败');
    }
  };

  // 删除对话
  const handleDeleteConversation = async (conversationId: string) => {
    // 防止重复删除
    if (deletingConversations.has(conversationId)) return;
    
    // 修复Set展开语法问题 - 使用Array.from
    setDeletingConversations(prev => new Set([...Array.from(prev), conversationId]));
    
    try {
      await deleteConversation(conversationId);
      
      // 如果删除的是当前对话，清空消息
      if (currentConversationId === conversationId) {
        setCurrentConversationId(null);
        setMessages([]);
      }
      
      // 重新加载对话列表
      loadConversations();
      antdMessage.success('对话删除成功');
    } catch (error: any) {
      console.error('删除对话失败:', error);
      antdMessage.error('删除对话失败');
    } finally {
      setDeletingConversations(prev => {
        const newSet = new Set(Array.from(prev));
        newSet.delete(conversationId);
        return newSet;
      });
    }
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

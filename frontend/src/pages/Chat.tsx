import React, { useState, useRef, useEffect } from 'react';
import {
  Input,
  Button,
  Typography,
  Tag,
  message as antdMessage,
  Spin,
  Dropdown,
  Menu,
  List,
  Select,
  Modal,
  Input as AntdInput,
  Tooltip,
  Layout,
  Avatar,
} from 'antd';
import {
  UserOutlined,
  SendOutlined,
  LogoutOutlined,
  PlusOutlined,
  DeleteOutlined,
  EditOutlined,
  DatabaseOutlined,
  TeamOutlined,
} from '@ant-design/icons';
import { 
  streamChatMessage, 
  getConversations, 
  getConversation, 
  updateConversationTitle, 
  deleteConversation,
  getAvailableModels 
} from '../api/chat';
import { useAuth } from '../context/AuthContext';
import MessageItem from '../components/MessageItem';
import { useNavigate } from 'react-router-dom';

const { Sider } = Layout;

const { TextArea } = Input;
const { Text } = Typography;

interface ReasoningStep {
  thought: string;
  action: string;
  action_input: string;
  observation: string;
}

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string; // for user message text OR assistant streaming chunks (unused)
  timestamp: Date;
  model?: string;
  reasoningSteps?: ReasoningStep[];
  finalAnswer?: string;
  thinking?: string; // interim thinking banner
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

/**
 * ChatInterface
 * -------------------------------------------------
 * 1. 实时流式显示 Step：后端每推送一条 `type: 'step'`，立即追加到 reasoningSteps
 * 2. 折叠 / 展开思考过程：使用 antd Collapse，每条 Assistant 消息各自维护 open / closed 状态
 * 3. 支持 Markdown 渲染（react-markdown）
 * -------------------------------------------------
 */
const ChatInterface: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const typeWriterTimer = useRef<NodeJS.Timeout | null>(null);
  
  // 新增状态
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string>('deepseek-chat');
  const [availableModels, setAvailableModels] = useState<Model[]>([]);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
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

  // 保持滚动在底部
  const scrollToBottom = () => {
    setTimeout(() => {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 80);
  };

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
    scrollToBottom();

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
              scrollToBottom();
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
              scrollToBottom();
              break;
            case 'step':
              // ✅ 每接收一步立刻追加，同时滚动到底部
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
              scrollToBottom();
              break;
            case 'final':
              // 打字机效果渲染 finalAnswer，保留之前实现
              let i = 0;
              const txt: string = obj.output || '';
              const typeWriter = () => {
                if (i <= txt.length) {
                  setMessages(prev => prev.map(m =>
                    m.id === lastMsgId ? { ...m, finalAnswer: txt.slice(0, i) } : m
                  ));
                  i++;
                  typeWriterTimer.current = setTimeout(typeWriter, 16);
                  scrollToBottom();
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
        scrollToBottom();
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
        const mostRecentConversation = data.conversations[0]; // 按更新时间排序，第一个是最新的
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

  // 回车发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendStreamMessage();
    }
  };



  /** 顶部用户栏 **/
  const userMenu = (
    <Menu>
      {user?.is_admin && (
        <>
          <Menu.Item key="admin" icon={<UserOutlined />} onClick={() => navigate('/admin')}>
            系统管理
          </Menu.Item>
          <Menu.Item key="vector" icon={<DatabaseOutlined />} onClick={() => navigate('/vector')}>
            向量数据库管理
          </Menu.Item>
          <Menu.Item key="feedback" icon={<TeamOutlined />} onClick={() => navigate('/feedback')}>
            人类反馈管理
          </Menu.Item>
          <Menu.Divider />
        </>
      )}
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={logout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  return (
    <Layout style={{ height: '100vh' }}>
      {/* 侧边栏 */}
      <Sider 
        width={300} 
        collapsible 
        collapsed={sidebarCollapsed}
        onCollapse={setSidebarCollapsed}
        style={{ background: '#fff', borderRight: '1px solid #f0f0f0' }}
      >
        <div style={{ padding: 16 }}>
          {/* 新对话按钮 */}
          <Button 
            type="primary" 
            icon={<PlusOutlined />} 
            onClick={createNewConversation}
            style={{ width: '100%', marginBottom: 16 }}
          >
            {!sidebarCollapsed && '新对话'}
          </Button>

          {/* 模型选择 */}
          {!sidebarCollapsed && (
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 12, color: '#666', marginBottom: 8 }}>选择模型</div>
              {loadingModels ? (
                <div style={{ 
                  padding: '8px 12px', 
                  background: '#f8f9fa', 
                  borderRadius: 6,
                  textAlign: 'center',
                  fontSize: 12,
                  color: '#666'
                }}>
                  <Spin size="small" /> 加载中...
                </div>
              ) : (
                <Select
                  value={selectedModel}
                  onChange={setSelectedModel}
                  style={{ width: '100%' }}
                  size="small"
                >
                  {availableModels.map(model => (
                    <Select.Option key={model.id} value={model.id}>
                      <Tooltip title={model.description}>
                        <span>{model.name}</span>
                      </Tooltip>
                    </Select.Option>
                  ))}
                </Select>
              )}
            </div>
          )}

          {/* 对话历史列表 */}
          <div style={{ 
            flex: 1, 
            overflowY: 'auto',
            marginTop: 16
          }}>
            {loadingConversations ? (
              <div style={{ 
                textAlign: 'center', 
                padding: 20
              }}>
                <Spin size="small" />
                <div style={{ marginTop: 8, fontSize: 12, color: '#666' }}>
                  加载对话历史中...
                </div>
              </div>
            ) : conversations.length === 0 ? (
              <div style={{ 
                textAlign: 'center', 
                color: '#b3b3b3', 
                fontSize: 14,
                padding: 20
              }}>
                暂无对话历史
              </div>
            ) : (
              <List
                size="small"
                dataSource={conversations}
                renderItem={(conversation) => (
                  <List.Item
                    style={{ 
                      padding: '12px 8px',
                      cursor: 'pointer',
                      backgroundColor: currentConversationId === conversation.id ? '#f0f8ff' : 'transparent',
                      borderRadius: 8,
                      marginBottom: 6,
                      border: currentConversationId === conversation.id ? '1px solid #1890ff' : '1px solid transparent',
                      transition: 'all 0.3s ease'
                    }}
                    onMouseEnter={(e) => {
                      if (currentConversationId !== conversation.id) {
                        e.currentTarget.style.backgroundColor = '#f8f9fa';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (currentConversationId !== conversation.id) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                      }
                    }}
                    onClick={() => loadConversation(conversation.id)}
                    actions={!sidebarCollapsed ? [
                      <Tooltip title="编辑标题">
                        <EditOutlined 
                          style={{ color: '#667eea' }}
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingConversation(conversation);
                            setNewTitle(conversation.title);
                            setEditTitleModal(true);
                          }}
                        />
                      </Tooltip>,
                      <Tooltip title="删除对话">
                        {deletingConversations.has(conversation.id) ? (
                          <Spin size="small" style={{ color: '#ff4d4f' }} />
                        ) : (
                          <DeleteOutlined 
                            style={{ color: '#ff4d4f' }}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteConversation(conversation.id);
                            }}
                          />
                        )}
                      </Tooltip>
                    ] : []}
                  >
                    <List.Item.Meta
                      title={
                        <div style={{ 
                          fontSize: 14, 
                          fontWeight: currentConversationId === conversation.id ? 600 : 400,
                          color: currentConversationId === conversation.id ? '#1890ff' : '#333',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap'
                        }}>
                          {conversation.title}
                        </div>
                      }
                      description={
                        !sidebarCollapsed ? (
                          <div style={{ fontSize: 12, color: '#666', marginTop: 4 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                              <span style={{ 
                                background: '#667eea', 
                                color: '#fff', 
                                padding: '2px 6px', 
                                borderRadius: 4, 
                                fontSize: 10 
                              }}>
                                {conversation.model_used}
                              </span>
                              <span>{conversation.message_count} 条消息</span>
                            </div>
                            <div style={{ marginTop: 2 }}>
                              {new Date(conversation.updated_at).toLocaleDateString('zh-CN')}
                            </div>
                          </div>
                        ) : null
                      }
                    />
                  </List.Item>
                )}
              />
            )}
          </div>
        </div>
      </Sider>

      {/* 主内容区域 */}
      <Layout>
        <div style={{ padding: '0 24px', height: '100vh', display: 'flex', flexDirection: 'column' }}>
          {/* 顶部栏 */}
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'space-between', 
            padding: '20px 0 16px 0',
            borderBottom: '1px solid #f0f0f0',
            marginBottom: 20
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <Avatar 
                icon={<UserOutlined />} 
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  boxShadow: '0 2px 8px rgba(102,126,234,0.3)'
                }} 
              />
              <div>
                <div style={{ fontWeight: 600, fontSize: 16, color: '#333' }}>
                  {user?.username}
                </div>
                <div style={{ fontSize: 12, color: '#666', marginTop: 2 }}>
                  {currentConversationId ? '正在对话中' : '准备开始新对话'}
                </div>
              </div>
              {user?.is_admin && (
                <Tag color="blue" style={{ marginLeft: 8 }}>
                  管理员
                </Tag>
              )}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
              <div style={{ 
                background: '#f8f9fa', 
                padding: '8px 12px', 
                borderRadius: 8,
                border: '1px solid #e9ecef'
              }}>
                <span style={{ fontSize: 12, color: '#666' }}>模型:</span>
                <span style={{ fontSize: 14, color: '#333', marginLeft: 4, fontWeight: 500 }}>
                  {availableModels.find(m => m.id === selectedModel)?.name || selectedModel}
                </span>
              </div>
              <Dropdown overlay={userMenu} placement="bottomRight">
                <Button 
                  type="text" 
                  icon={<LogoutOutlined />} 
                  style={{ 
                    color: '#667eea', 
                    fontWeight: 600,
                    borderRadius: 8,
                    padding: '8px 16px'
                  }}
                >
                  退出
                </Button>
              </Dropdown>
            </div>
          </div>

          {/* 消息列表区域 */}
          <div style={{ 
            flex: 1, 
            background: '#fff', 
            borderRadius: 16, 
            boxShadow: '0 2px 12px rgba(102,126,234,0.06)', 
            padding: '32px 18px 18px', 
            marginBottom: 18, 
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column'
          }}>
            {messages.length === 0 && (
              <div style={{ 
                textAlign: 'center', 
                color: '#b3b3b3', 
                marginTop: 80, 
                fontSize: 16,
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <div>
                  <div style={{ fontSize: 24, marginBottom: 16, color: '#667eea' }}>🧪</div>
                  <div>你好，{user?.username}！</div>
                  <div>请在下方输入你的化学问题</div>
                </div>
              </div>
            )}
            {messages.length > 0 && (
              <div style={{ flex: 1 }}>
                {messages.map(msg => (
                  <MessageItem key={msg.id} msg={msg} copyMessage={copyMessage} />
                ))}
              </div>
            )}
            <div ref={chatEndRef} />
            {loading && (
              <div style={{ textAlign: 'center', padding: 20 }}>
                <Spin />
                <Text style={{ color: '#667eea', marginLeft: 12 }}>模型思考中…</Text>
              </div>
            )}
          </div>

          {/* 输入区 */}
          <div style={{ 
            display: 'flex', 
            gap: 12, 
            paddingBottom: 24,
            background: '#fff',
            borderRadius: 16,
            padding: 20,
            boxShadow: '0 2px 12px rgba(102,126,234,0.06)'
          }}>
            <TextArea
              value={inputValue}
              onChange={e => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的化学问题，例如：计算苯的分子量、分析乙醇的化学性质、预测化学反应产物… (按 Enter 发送，Shift+Enter 换行)"
              autoSize={{ minRows: 2, maxRows: 6 }}
              style={{ 
                resize: 'none', 
                fontSize: 15, 
                borderRadius: 12, 
                background: '#f8f9fa',
                border: '1px solid #e9ecef',
                transition: 'all 0.3s ease'
              }}
              disabled={loading || streaming}
            />
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={sendStreamMessage}
                loading={loading}
                disabled={!inputValue.trim() || loading || streaming}
                size="large"
                style={{ 
                  borderRadius: 12, 
                  minWidth: 80, 
                  height: 'auto',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  boxShadow: '0 4px 12px rgba(102,126,234,0.3)'
                }}
              >
                发送
              </Button>
              <Button
                onClick={clearChat}
                size="large"
                disabled={loading || streaming || messages.length === 0}
                style={{ 
                  borderRadius: 12, 
                  minWidth: 80, 
                  background: '#f8f9fa', 
                  color: '#6c757d', 
                  border: '1px solid #e9ecef',
                  transition: 'all 0.3s ease'
                }}
              >
                清空
              </Button>
            </div>
          </div>
        </div>
      </Layout>

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
    </Layout>
  );
};

export default ChatInterface;

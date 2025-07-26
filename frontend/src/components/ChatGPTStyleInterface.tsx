import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Input,
  Button,
  Typography,
  Spin,
  Layout,
  Avatar,
  Dropdown,
  Menu,
  Tooltip,
  List,
} from 'antd';
import {
  UserOutlined,
  SendOutlined,
  LogoutOutlined,
  PlusOutlined,
  RobotOutlined,
  CopyOutlined,
  DownOutlined,
  DeleteOutlined,
  EditOutlined,
  MoreOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import EnhancedContentParser from './EnhancedContentParser';
import { useAuth } from '../context/AuthContext';
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

interface ChatGPTStyleInterfaceProps {
  messages: Message[];
  inputValue: string;
  setInputValue: (value: string) => void;
  onSendMessage: () => void;
  loading: boolean;
  streaming: boolean;
  copyMessage: (content: string) => void;
  clearChat: () => void;
  selectedModel: string;
  availableModels: any[];
  onModelChange: (model: string) => void;
  // 新增对话管理相关props
  conversations: Conversation[];
  currentConversationId: string | null;
  onConversationSelect: (conversationId: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (conversationId: string) => void;
  onEditConversationTitle: (conversation: Conversation) => void;
  loadingConversations: boolean;
}

const ChatGPTStyleInterface: React.FC<ChatGPTStyleInterfaceProps> = ({
  messages,
  inputValue,
  setInputValue,
  onSendMessage,
  loading,
  streaming,
  copyMessage,
  clearChat,
  selectedModel,
  availableModels,
  onModelChange,
  conversations,
  currentConversationId,
  onConversationSelect,
  onNewConversation,
  onDeleteConversation,
  onEditConversationTitle,
  loadingConversations,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [collapsedSteps, setCollapsedSteps] = useState<Set<string>>(new Set());
  const [siderWidth, setSiderWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);

  // 保持滚动在底部
  const scrollToBottom = () => {
    setTimeout(() => {
      chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 回车发送
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  // 切换思考步骤的展开/折叠
  const toggleSteps = (messageId: string) => {
    setCollapsedSteps(prev => {
      const newSet = new Set(prev);
      if (newSet.has(messageId)) {
        newSet.delete(messageId);
      } else {
        newSet.add(messageId);
      }
      return newSet;
    });
  };

  // 处理拖拽调整大小
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const newWidth = e.clientX;
    // 限制最小和最大宽度
    if (newWidth >= 250 && newWidth <= 500) {
      setSiderWidth(newWidth);
    }
  }, [isResizing]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  // 添加全局鼠标事件监听
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  // 格式化时间
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
    
    if (diffInHours < 24) {
      return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
    } else {
      return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' });
    }
  };

  // 对话项操作菜单
  const getConversationMenu = (conversation: Conversation) => (
    <Menu>
      <Menu.Item 
        key="edit" 
        icon={<EditOutlined />}
        onClick={() => onEditConversationTitle(conversation)}
      >
        重命名
      </Menu.Item>
      <Menu.Item 
        key="delete" 
        icon={<DeleteOutlined />}
        onClick={() => onDeleteConversation(conversation.id)}
        danger
      >
        删除
      </Menu.Item>
    </Menu>
  );

  // 渲染思考步骤
  const renderReasoningSteps = (steps?: ReasoningStep[]) => {
    if (!steps?.length) return null;
    
    return (
      <div style={{ 
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)', 
        borderRadius: 12, 
        padding: 16, 
        marginTop: 12,
        border: '1px solid #e2e8f0',
        boxShadow: '0 2px 8px rgba(0,0,0,0.04)'
      }}>
        <div style={{
          fontSize: 14,
          fontWeight: 600,
          color: '#475569',
          marginBottom: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 8
        }}>
          <span style={{ 
            width: 6, 
            height: 6, 
            borderRadius: '50%', 
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
          }}></span>
          推理过程
        </div>
        {steps.map((step, idx) => (
          <div key={idx} style={{ 
            marginBottom: idx < steps.length - 1 ? 16 : 0,
            padding: 16,
            background: '#ffffff',
            borderRadius: 10,
            border: '1px solid #e2e8f0',
            boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
            position: 'relative'
          }}>
            {/* 步骤编号 */}
            <div style={{
              position: 'absolute',
              top: -8,
              left: 16,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              borderRadius: 12,
              padding: '4px 12px',
              fontSize: 12,
              fontWeight: 600
            }}>
              步骤 {idx + 1}
            </div>
            
            <div style={{ marginTop: 8 }}>
              {/* 思考部分 */}
              <div style={{ marginBottom: 12 }}>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 8, 
                  marginBottom: 8 
                }}>
                  <span style={{ 
                    fontSize: 16,
                    filter: 'grayscale(0.3)'
                  }}>🤔</span>
                  <strong style={{ 
                    color: '#3b82f6', 
                    fontSize: 14,
                    fontWeight: 600
                  }}>思考</strong>
                </div>
                <div style={{ 
                  marginLeft: 24, 
                  fontSize: 14,
                  lineHeight: 1.6,
                  color: '#475569'
                }}>
                  {step.thought}
                </div>
              </div>

              {/* 行动和输入 */}
              <div style={{ 
                display: 'grid', 
                gridTemplateColumns: '1fr 1fr', 
                gap: 16, 
                marginBottom: 12 
              }}>
                <div>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 8, 
                    marginBottom: 6 
                  }}>
                    <span style={{ fontSize: 14 }}>⚡</span>
                    <strong style={{ 
                      color: '#10b981', 
                      fontSize: 13,
                      fontWeight: 600
                    }}>行动</strong>
                  </div>
                  <div style={{ 
                    marginLeft: 22, 
                    fontSize: 13,
                    color: '#64748b',
                    fontFamily: 'Monaco, Consolas, monospace',
                    background: '#f8fafc',
                    padding: '6px 10px',
                    borderRadius: 6,
                    border: '1px solid #e2e8f0'
                  }}>
                    {step.action}
                  </div>
                </div>
                
                <div>
                  <div style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: 8, 
                    marginBottom: 6 
                  }}>
                    <span style={{ fontSize: 14 }}>📝</span>
                    <strong style={{ 
                      color: '#f59e0b', 
                      fontSize: 13,
                      fontWeight: 600
                    }}>输入</strong>
                  </div>
                  <div style={{ 
                    marginLeft: 22, 
                    fontSize: 13,
                    color: '#64748b',
                    fontFamily: 'Monaco, Consolas, monospace',
                    background: '#f8fafc',
                    padding: '6px 10px',
                    borderRadius: 6,
                    border: '1px solid #e2e8f0',
                    wordBreak: 'break-all'
                  }}>
                    {step.action_input}
                  </div>
                </div>
              </div>

              {/* 观察结果 */}
              <div>
                <div style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 8, 
                  marginBottom: 8 
                }}>
                  <span style={{ fontSize: 16 }}>👁️</span>
                  <strong style={{ 
                    color: '#8b5cf6', 
                    fontSize: 14,
                    fontWeight: 600
                  }}>观察结果</strong>
                </div>
                <div style={{ 
                  marginLeft: 24, 
                  fontSize: 14,
                  lineHeight: 1.6,
                  color: '#475569',
                  background: '#fafbfc',
                  padding: 12,
                  borderRadius: 8,
                  border: '1px solid #e2e8f0'
                }}>
                  <ReactMarkdown 
                     remarkPlugins={[remarkGfm]}
                     components={{
                       p: ({ children }) => <div style={{ margin: '8px 0' }}>{children}</div>,
                       code: ({ children, className }) => {
                         const isInline = !className;
                         return isInline ? (
                           <code style={{
                             background: '#f1f5f9',
                             padding: '2px 6px',
                             borderRadius: 4,
                             fontSize: 13,
                             fontFamily: 'Monaco, Consolas, monospace',
                             color: '#e11d48'
                           }}>
                             {children}
                           </code>
                         ) : (
                           <pre style={{
                             background: '#1e293b',
                             color: '#e2e8f0',
                             padding: 12,
                             borderRadius: 6,
                             overflow: 'auto',
                             fontSize: 13,
                             fontFamily: 'Monaco, Consolas, monospace'
                           }}>
                             <code>{children}</code>
                           </pre>
                         );
                       }
                     }}
                   >
                     {step.observation}
                   </ReactMarkdown>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  // 用户菜单
  const userMenu = (
    <Menu>
      <Menu.Item key="profile" icon={<UserOutlined />} onClick={() => navigate('/profile')}>
        个人信息
      </Menu.Item>
      {user?.is_admin && (
        <>
          <Menu.Divider />
          <Menu.Item key="admin" icon={<UserOutlined />} onClick={() => navigate('/admin')}>
            系统管理
          </Menu.Item>
        </>
      )}
      <Menu.Divider />
      <Menu.Item key="logout" icon={<LogoutOutlined />} onClick={logout}>
        退出登录
      </Menu.Item>
    </Menu>
  );

  return (
    <Layout style={{ height: '100vh', background: '#f8fafc' }}>
      {/* 左侧对话记录面板 */}
      <Layout.Sider 
        width={siderWidth} 
        style={{ 
          background: '#ffffff',
          borderRight: '1px solid #e2e8f0',
          boxShadow: '2px 0 8px rgba(0,0,0,0.04)',
          position: 'relative'
        }}
      >
        <div style={{ 
          height: '100%', 
          display: 'flex', 
          flexDirection: 'column',
          padding: '16px'
        }}>
          {/* 新建对话按钮 */}
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={onNewConversation}
            size="large"
            style={{
              marginBottom: 16,
              borderRadius: 12,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              boxShadow: '0 4px 12px rgba(102,126,234,0.25)',
              height: 48,
              fontSize: 15,
              fontWeight: 600
            }}
          >
            新建对话
          </Button>

          {/* 对话列表 */}
          <div style={{ 
            flex: 1, 
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <div style={{ 
              marginBottom: 12,
              color: '#64748b',
              fontSize: 13,
              fontWeight: 500,
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}>
              对话记录
            </div>
            
            <div style={{ 
              flex: 1, 
              overflow: 'auto',
              marginRight: -8,
              paddingRight: 8
            }}>
              {loadingConversations ? (
                <div style={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  height: 100
                }}>
                  <Spin />
                </div>
              ) : conversations.length === 0 ? (
                <div style={{
                  textAlign: 'center',
                  color: '#94a3b8',
                  fontSize: 14,
                  marginTop: 40
                }}>
                  暂无对话记录
                </div>
              ) : (
                <List
                  dataSource={conversations}
                  renderItem={(conversation) => (
                    <div
                      key={conversation.id}
                      onClick={() => onConversationSelect(conversation.id)}
                      style={{
                         padding: '12px 16px',
                         marginBottom: 8,
                         borderRadius: 12,
                         cursor: 'pointer',
                         background: currentConversationId === conversation.id 
                           ? 'linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%)' 
                           : 'transparent',
                         border: currentConversationId === conversation.id 
                           ? '1px solid #cbd5e1' 
                           : '1px solid transparent',
                         transition: 'all 0.2s ease',
                         position: 'relative'
                       }}
                      onMouseEnter={(e) => {
                        if (currentConversationId !== conversation.id) {
                          e.currentTarget.style.background = '#f8fafc';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (currentConversationId !== conversation.id) {
                          e.currentTarget.style.background = 'transparent';
                        }
                      }}
                    >
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'flex-start',
                        justifyContent: 'space-between'
                      }}>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{
                            fontSize: 14,
                            fontWeight: 500,
                            color: '#1e293b',
                            marginBottom: 4,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}>
                            {conversation.title}
                          </div>
                          <div style={{
                            fontSize: 12,
                            color: '#64748b',
                            display: 'flex',
                            alignItems: 'center',
                            gap: 8
                          }}>
                            <span>{formatTime(conversation.updated_at)}</span>
                            <span>•</span>
                            <span>{conversation.message_count} 条消息</span>
                          </div>
                        </div>
                        
                        <Dropdown 
                          overlay={getConversationMenu(conversation)} 
                          trigger={['click']}
                          placement="bottomRight"
                        >
                          <Button
                            type="text"
                            icon={<MoreOutlined />}
                            size="small"
                            onClick={(e) => e.stopPropagation()}
                            style={{
                              opacity: 0.6,
                              transition: 'opacity 0.2s ease'
                            }}
                            onMouseEnter={(e) => {
                              e.currentTarget.style.opacity = '1';
                            }}
                            onMouseLeave={(e) => {
                              e.currentTarget.style.opacity = '0.6';
                            }}
                          />
                        </Dropdown>
                      </div>
                    </div>
                  )}
                />
              )}
            </div>
          </div>

          {/* 用户信息区域 */}
          <div style={{
            borderTop: '1px solid #e2e8f0',
            paddingTop: 16,
            marginTop: 16
          }}>
            <Dropdown overlay={userMenu} placement="topRight">
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                cursor: 'pointer',
                padding: '12px 16px',
                borderRadius: 12,
                transition: 'background-color 0.2s',
                background: '#f8fafc'
              }}>
                <Avatar 
                  icon={<UserOutlined />} 
                  style={{ 
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    fontSize: 16
                  }} 
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ 
                    fontSize: 14, 
                    fontWeight: 500,
                    color: '#1e293b',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}>
                    {user?.username}
                  </div>
                  <div style={{ 
                    fontSize: 12, 
                    color: '#64748b'
                  }}>
                    {user?.is_admin ? '管理员' : '用户'}
                  </div>
                </div>
              </div>
            </Dropdown>
          </div>
        </div>
      </Layout.Sider>

      {/* 拖拽分割线 */}
      <div
        onMouseDown={handleMouseDown}
        style={{
          width: 4,
          background: isResizing ? '#667eea' : 'transparent',
          cursor: 'col-resize',
          position: 'relative',
          zIndex: 1001,
          transition: isResizing ? 'none' : 'background-color 0.2s ease'
        }}
        onMouseEnter={(e) => {
          if (!isResizing) {
            e.currentTarget.style.background = '#e2e8f0';
          }
        }}
        onMouseLeave={(e) => {
          if (!isResizing) {
            e.currentTarget.style.background = 'transparent';
          }
        }}
      />

      {/* 右侧主聊天区域 */}
      <Layout style={{ background: '#ffffff' }}>
        {/* 顶部导航栏 */}
        <div style={{
          height: 64,
          background: '#ffffff',
          borderBottom: '1px solid #e2e8f0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 24px',
          position: 'sticky',
          top: 0,
          zIndex: 1000,
          boxShadow: '0 1px 3px rgba(0,0,0,0.04)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <div style={{
              width: 36,
              height: 36,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              borderRadius: 10,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontSize: 18,
              fontWeight: 'bold'
            }}>
              🧪
            </div>
            <div>
              <div style={{ 
                fontSize: 18, 
                fontWeight: 600, 
                color: '#1e293b',
                marginBottom: 2
              }}>
                化学智能助手
              </div>
              <div style={{ 
                fontSize: 13, 
                color: '#64748b'
              }}>
                专业的化学问题解答助手
              </div>
            </div>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            {/* 模型选择 */}
            <Tooltip title="选择模型">
              <select
                value={selectedModel}
                onChange={(e) => onModelChange(e.target.value)}
                style={{
                  padding: '8px 12px',
                  border: '1px solid #e2e8f0',
                  borderRadius: 8,
                  fontSize: 14,
                  background: '#f8fafc',
                  cursor: 'pointer',
                  color: '#475569',
                  fontWeight: 500
                }}
              >
                {availableModels.map(model => (
                  <option key={model.id} value={model.id}>
                    {model.name}
                  </option>
                ))}
              </select>
            </Tooltip>
          </div>
        </div>

        {/* 聊天内容区域 */}
        <div style={{
          flex: 1,
          overflow: 'auto',
          padding: '24px',
          background: '#f8fafc'
        }}>
          {messages.length === 0 && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center'
            }}>
              <div style={{
                width: 96,
                height: 96,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: 40,
                marginBottom: 32,
                boxShadow: '0 12px 32px rgba(102,126,234,0.25)'
              }}>
                🧪
              </div>
              <Typography.Title level={3} style={{ 
                marginBottom: 16, 
                color: '#1e293b',
                fontWeight: 600
              }}>
                欢迎使用化学智能助手
              </Typography.Title>
              <Typography.Text style={{ 
                fontSize: 16, 
                color: '#64748b', 
                maxWidth: 480,
                lineHeight: 1.6
              }}>
                我可以帮助您解答化学问题、计算分子性质、预测反应产物、分析化学结构等。请输入您的问题开始对话。
              </Typography.Text>
            </div>
          )}

              <div style={{ maxWidth: 800, margin: '0 auto' }}>
                {messages.map((msg, index) => (
                  <div
                    key={msg.id}
                    style={{
                      display: 'flex',
                      justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
                      marginBottom: 32,
                      alignItems: 'flex-start'
                    }}
                  >
                    {msg.type === 'assistant' && (
                      <Avatar 
                        icon={<RobotOutlined />} 
                        style={{ 
                          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                          marginRight: 16,
                          marginTop: 4,
                          width: 36,
                          height: 36
                        }} 
                      />
                    )}

                    <div
                      style={{
                        maxWidth: '75%',
                        background: msg.type === 'user' 
                          ? 'linear-gradient(135deg, #1890ff 0%, #67e8f9 100%)' 
                          : '#ffffff',
                        color: msg.type === 'user' ? '#ffffff' : '#1e293b',
                        borderRadius: msg.type === 'user' 
                          ? '20px 20px 6px 20px' 
                          : '20px 20px 20px 6px',
                        padding: '16px 20px',
                        boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                        position: 'relative',
                        border: msg.type === 'assistant' ? '1px solid #e2e8f0' : 'none',
                        fontSize: 15,
                        lineHeight: 1.6
                      }}
                    >
                      {msg.type === 'assistant' ? (
                        <div>
                          {/* 思考过程 */}
                          {msg.thinking && (
                            <div style={{ 
                              marginBottom: 16,
                              padding: '12px 16px',
                              background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)',
                              borderRadius: 12,
                              border: '1px solid #e2e8f0'
                            }}>
                              <div style={{ 
                                fontSize: 13, 
                                color: '#667eea', 
                                fontWeight: 600,
                                marginBottom: 8,
                                display: 'flex',
                                alignItems: 'center',
                                gap: 6
                              }}>
                                🤔 思考过程
                              </div>
                              <div style={{ 
                                fontSize: 13, 
                                color: '#64748b',
                                lineHeight: 1.5
                              }}>
                                <EnhancedContentParser 
                                  content={msg.thinking} 
                                  enableMarkdown={false}
                                  enableChemicalDetection={false}
                                />
                              </div>
                            </div>
                          )}

                          {/* 推理步骤 */}
                          {msg.reasoningSteps && msg.reasoningSteps.length > 0 && (
                            <div style={{ marginBottom: 16 }}>
                              <Button
                                type="link"
                                size="small"
                                icon={<DownOutlined rotate={collapsedSteps.has(msg.id) ? 0 : 180} />}
                                onClick={() => toggleSteps(msg.id)}
                                style={{ 
                                  padding: 0, 
                                  height: 'auto', 
                                  color: '#667eea',
                                  fontSize: 13,
                                  fontWeight: 500,
                                  marginBottom: 8
                                }}
                              >
                                {collapsedSteps.has(msg.id) ? '展开推理过程' : '折叠推理过程'}
                              </Button>
                              
                              {!collapsedSteps.has(msg.id) && (
                                <div style={{
                                  background: 'linear-gradient(135deg, #fafbfc 0%, #f6f8fa 100%)',
                                  borderRadius: 12,
                                  border: '1px solid #e1e4e8',
                                  padding: '12px 16px'
                                }}>
                                  {renderReasoningSteps(msg.reasoningSteps)}
                                </div>
                              )}
                            </div>
                          )}

                          {/* 最终答案 */}
                          {msg.finalAnswer && (
                            <div style={{ 
                              background: '#ffffff',
                              borderRadius: 8,
                              padding: '16px 0'
                            }}>
                              <EnhancedContentParser 
                                content={msg.finalAnswer}
                                enableMarkdown={true}
                                enableChemicalDetection={true}
                              />
                            </div>
                          )}
                        </div>
                      ) : (
                        <div style={{ 
                          background: 'rgba(255,255,255,0.1)',
                          borderRadius: 8,
                          padding: '8px 0'
                        }}>
                          <EnhancedContentParser 
                            content={msg.content}
                            enableMarkdown={true}
                            enableChemicalDetection={true}
                          />
                        </div>
                      )}

                      {/* 复制按钮 */}
                      <Button
                        type="text"
                        size="small"
                        icon={<CopyOutlined />}
                        onClick={() => copyMessage(msg.type === 'assistant' ? (msg.finalAnswer || '') : msg.content)}
                        style={{
                          position: 'absolute',
                          top: 8,
                          right: 8,
                          color: msg.type === 'user' ? 'rgba(255,255,255,0.8)' : '#64748b',
                          background: msg.type === 'user' ? 'rgba(255,255,255,0.1)' : 'rgba(100,116,139,0.1)',
                          borderRadius: '50%',
                          width: 28,
                          height: 28,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          opacity: 0.7,
                          transition: 'opacity 0.2s ease'
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.opacity = '1';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.opacity = '0.7';
                        }}
                      />
                    </div>

                    {msg.type === 'user' && (
                      <Avatar 
                        icon={<UserOutlined />} 
                        style={{ 
                          background: 'linear-gradient(135deg, #1890ff 0%, #67e8f9 100%)',
                          marginLeft: 16,
                          marginTop: 4,
                          width: 36,
                          height: 36
                        }} 
                      />
                    )}
                  </div>
                ))}
                
                {/* 加载状态 */}
                {loading && (
                  <div style={{
                    display: 'flex',
                    justifyContent: 'flex-start',
                    marginBottom: 32
                  }}>
                    <Avatar 
                      icon={<RobotOutlined />} 
                      style={{ 
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        marginRight: 16,
                        marginTop: 4,
                        width: 36,
                        height: 36
                      }} 
                    />
                    <div style={{
                      background: '#ffffff',
                      borderRadius: '20px 20px 20px 6px',
                      padding: '16px 20px',
                      boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: 12,
                      border: '1px solid #e2e8f0'
                    }}>
                      <Spin size="small" />
                      <Typography.Text style={{ color: '#667eea', fontSize: 14, fontWeight: 500 }}>
                        {streaming ? '正在思考中...' : '处理中...'}
                      </Typography.Text>
                    </div>
                  </div>
                )}
              </div>
              
          <div ref={chatEndRef} />
        </div>

        {/* 底部输入区域 */}
        <div style={{
          background: '#ffffff',
          borderTop: '1px solid #e2e8f0',
          padding: '20px 24px',
          position: 'sticky',
          bottom: 0,
          zIndex: 1000
        }}>
          <div style={{
            maxWidth: 800,
            margin: '0 auto',
            display: 'flex',
            gap: 12,
            alignItems: 'flex-end'
          }}>
            <div style={{ flex: 1 }}>
              <Input.TextArea
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入您的化学问题，例如：计算苯的分子量、分析乙醇的化学性质、预测化学反应产物… (按 Enter 发送，Shift+Enter 换行)"
                autoSize={{ minRows: 2, maxRows: 6 }}
                style={{
                  resize: 'none',
                  fontSize: 15,
                  borderRadius: 16,
                  border: '1px solid #e2e8f0',
                  background: '#f8fafc',
                  transition: 'all 0.3s ease',
                  padding: '12px 16px'
                }}
                disabled={loading || streaming}
              />
            </div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={onSendMessage}
                loading={loading}
                disabled={!inputValue.trim() || loading || streaming}
                size="large"
                style={{
                  borderRadius: 16,
                  minWidth: 80,
                  height: 'auto',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  boxShadow: '0 4px 12px rgba(102,126,234,0.25)',
                  padding: '12px 20px',
                  fontWeight: 600
                }}
              >
                发送
              </Button>
              
              {messages.length > 0 && (
                <Button
                  onClick={clearChat}
                  size="large"
                  disabled={loading || streaming}
                  style={{
                    borderRadius: 16,
                    minWidth: 80,
                    background: '#f8fafc',
                    color: '#64748b',
                    border: '1px solid #e2e8f0',
                    transition: 'all 0.3s ease',
                    padding: '8px 16px',
                    fontWeight: 500
                  }}
                >
                  清空
                </Button>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </Layout>
  );
};

export default ChatGPTStyleInterface;
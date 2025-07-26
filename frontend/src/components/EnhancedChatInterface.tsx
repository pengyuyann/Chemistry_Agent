import React, { useState, useRef, useEffect } from 'react';
import {
  Layout,
  Input,
  Button,
  Spin,
  message,
  Space,
  Typography,
  Card,
  Divider,
  Tooltip,
  Badge,
} from 'antd';
import {
  SendOutlined,
  ExperimentOutlined,
  ToolOutlined,
  ClearOutlined,
  DownloadOutlined,
  UploadOutlined,
} from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { streamChatMessage } from '../api/chat';
import EnhancedMessageItem from './EnhancedMessageItem';
import ChemicalToolPanel from './ChemicalToolPanel';

const { Content, Sider } = Layout;
const { TextArea } = Input;
const { Title, Text } = Typography;

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

const EnhancedChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showChemicalTools, setShowChemicalTools] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user, logout } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingMessage]);

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
    message.success('已复制到剪贴板');
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    // 检查用户是否已登录
    if (!user) {
      message.error('请先登录');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setStreamingMessage('');

    try {
      let finalContent = '';
      
      await new Promise<void>((resolve, reject) => {
        streamChatMessage(
          {
            input: inputValue,
            conversation_id: null,
            model: 'deepseek-chat',
            tools_model: 'deepseek-chat',
            temperature: 0.1,
            max_iterations: 15,
            streaming: true,
            local_rxn: false,
            api_keys: {},
          },
          (chunk) => {
            setStreamingMessage(prev => prev + chunk);
            finalContent += chunk;
          },
          () => {
            // 流结束时的处理
            const assistantMessage: Message = {
              id: (Date.now() + 1).toString(),
              type: 'assistant',
              content: finalContent,
              timestamp: new Date(),
            };

            setMessages(prev => [...prev, assistantMessage]);
            setStreamingMessage('');
            resolve();
          },
          (error) => {
            console.error('Stream error:', error);
            // 检查是否是认证错误
            if (error && error.message && error.message.includes('401')) {
              message.error('登录已过期，请重新登录');
              logout();
            } else {
              message.error('发送消息失败，请重试');
            }
            reject(error);
          }
        );
      });
    } catch (error) {
      console.error('Chat error:', error);
      // 错误已经在onError回调中处理了
    } finally {
      setIsLoading(false);
    }
  };

  const handleToolUse = (tool: string, input: string) => {
    const toolMessage = `请使用${tool}工具分析: ${input}`;
    setInputValue(toolMessage);
    setShowChemicalTools(false);
  };

  const clearChat = () => {
    setMessages([]);
    setStreamingMessage('');
    message.success('聊天记录已清空');
  };

  const exportChat = () => {
    const chatData = {
      timestamp: new Date().toISOString(),
      user: user?.username,
      messages: messages,
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chemistry-chat-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    message.success('聊天记录已导出');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Layout style={{ height: '100vh' }}>
      <Sider 
        width={300} 
        style={{ 
          background: '#fff',
          borderRight: '1px solid #f0f0f0',
          overflow: 'auto'
        }}
      >
        <div style={{ padding: '16px' }}>
          <Title level={4} style={{ marginBottom: '16px', textAlign: 'center' }}>
            <ExperimentOutlined style={{ color: '#1890ff', marginRight: 8 }} />
            化学助手
          </Title>
          
          <ChemicalToolPanel onToolUse={handleToolUse} />
          
          <Card size="small" style={{ marginBottom: 16 }}>
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button 
                type="primary" 
                icon={<ToolOutlined />}
                onClick={() => setShowChemicalTools(!showChemicalTools)}
                block
              >
                {showChemicalTools ? '隐藏' : '显示'}化学工具
              </Button>
              
              <Button 
                icon={<ClearOutlined />}
                onClick={clearChat}
                block
              >
                清空聊天
              </Button>
              
              <Button 
                icon={<DownloadOutlined />}
                onClick={exportChat}
                block
              >
                导出聊天
              </Button>
            </Space>
          </Card>
          
          <Divider />
          
          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              欢迎使用化学智能助手！
              <br />
              我可以帮助您进行分子分析、反应预测、安全性检查等化学相关任务。
            </Text>
          </div>
        </div>
      </Sider>
      
      <Layout>
        <Content style={{ 
          display: 'flex', 
          flexDirection: 'column',
          background: '#f5f5f5'
        }}>
          {/* 消息区域 */}
          <div style={{ 
            flex: 1, 
            overflow: 'auto', 
            padding: '20px',
            background: '#fff',
            margin: '16px',
            borderRadius: '8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            {messages.length === 0 && !isLoading && (
              <div style={{ 
                textAlign: 'center', 
                marginTop: '100px',
                color: '#666'
              }}>
                <ExperimentOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
                <Title level={3}>开始您的化学探索之旅</Title>
                <Text type="secondary">
                  您可以询问关于分子结构、化学反应、安全性分析等问题
                </Text>
              </div>
            )}
            
            {messages.map((msg) => (
              <EnhancedMessageItem
                key={msg.id}
                msg={msg}
                copyMessage={copyMessage}
              />
            ))}
            
            {isLoading && streamingMessage && (
              <div style={{
                display: 'flex',
                justifyContent: 'flex-start',
                marginBottom: 18,
              }}>
                <div style={{
                  maxWidth: '75%',
                  background: 'linear-gradient(135deg, #f5f6fa 0%, #e0e7ff 100%)',
                  color: '#333',
                  borderRadius: '18px 18px 18px 4px',
                  boxShadow: '0 2px 8px rgba(102,126,234,0.08)',
                  padding: '14px 18px',
                  fontSize: 15,
                  position: 'relative',
                  wordBreak: 'break-word',
                }}>
                  <Spin size="small" style={{ marginRight: 8 }} />
                  {streamingMessage}
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
          
          {/* 输入区域 */}
          <div style={{ 
            padding: '20px',
            background: '#fff',
            borderTop: '1px solid #f0f0f0'
          }}>
            <div style={{ 
              display: 'flex', 
              gap: '12px',
              alignItems: 'flex-end'
            }}>
              <TextArea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="输入您的化学问题... (Shift+Enter换行，Enter发送)"
                autoSize={{ minRows: 1, maxRows: 4 }}
                style={{ flex: 1 }}
                disabled={isLoading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={handleSendMessage}
                loading={isLoading}
                disabled={!inputValue.trim()}
                style={{ height: '40px' }}
              >
                发送
              </Button>
            </div>
            
            <div style={{ marginTop: '8px', textAlign: 'center' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                支持分子结构分析、反应预测、安全性检查等化学工具
              </Text>
            </div>
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default EnhancedChatInterface; 
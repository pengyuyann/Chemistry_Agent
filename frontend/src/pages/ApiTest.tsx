import React, { useState } from 'react';
import {
  Card,
  Button,
  Input,
  Typography,
  Space,
  Alert,
  Divider,
  message,
} from 'antd';
import { ExperimentOutlined, SendOutlined } from '@ant-design/icons';
import { streamChatMessage } from '../api/chat';
import { useAuth } from '../context/AuthContext';

const { TextArea } = Input;
const { Title, Text } = Typography;

const ApiTest: React.FC = () => {
  const [inputValue, setInputValue] = useState('计算苯的分子量');
  const [response, setResponse] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const { user } = useAuth();

  const testApi = async () => {
    if (!inputValue.trim()) {
      message.error('请输入测试内容');
      return;
    }

    if (!user) {
      message.error('请先登录');
      return;
    }

    setLoading(true);
    setResponse('');
    setError('');

    try {
      let finalResponse = '';
      
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
            console.log('Received chunk:', chunk);
            setResponse(prev => prev + chunk);
            finalResponse += chunk;
          },
          () => {
            console.log('Stream completed');
            resolve();
          },
          (error) => {
            console.error('Stream error:', error);
            setError(error.message || '未知错误');
            reject(error);
          }
        );
      });
      
      message.success('API测试成功');
    } catch (error) {
      console.error('Test error:', error);
      setError(error instanceof Error ? error.message : '未知错误');
      message.error('API测试失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '800px', margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        <ExperimentOutlined style={{ color: '#1890ff', marginRight: '12px' }} />
        API连接测试
      </Title>

      <Card title="用户信息" style={{ marginBottom: '24px' }}>
        <Space direction="vertical">
          <Text>用户名: {user?.username || '未登录'}</Text>
          <Text>用户ID: {user?.id || 'N/A'}</Text>
          <Text>管理员: {user?.is_admin ? '是' : '否'}</Text>
        </Space>
      </Card>

      <Card title="API测试" style={{ marginBottom: '24px' }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>测试输入:</Text>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="输入要测试的化学问题..."
              rows={3}
              style={{ marginTop: 8 }}
            />
          </div>
          
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={testApi}
            loading={loading}
            disabled={!user}
            block
          >
            测试API连接
          </Button>
        </Space>
      </Card>

      {error && (
        <Alert
          message="错误信息"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '24px' }}
        />
      )}

      {response && (
        <Card title="API响应">
          <div style={{ 
            background: '#f5f5f5', 
            padding: '16px', 
            borderRadius: '8px',
            fontFamily: 'monospace',
            fontSize: '14px',
            whiteSpace: 'pre-wrap',
            maxHeight: '400px',
            overflowY: 'auto'
          }}>
            {response}
          </div>
        </Card>
      )}

      <Divider />

      <Alert
        message="调试信息"
        description="此页面用于测试API连接和调试问题。如果遇到422错误，请检查请求格式和用户认证状态。"
        type="info"
        showIcon
      />
    </div>
  );
};

export default ApiTest; 
import React, { useState } from 'react';
import {
  Avatar,
  Button,
  Collapse,
} from 'antd';
import {
  CopyOutlined,
  DownOutlined,
  RobotOutlined,
  UserOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';

const { Panel } = Collapse;

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

const renderReasoningSteps = (steps?: ReasoningStep[]) => {
  if (!steps?.length) return null;
  return (
    <Collapse ghost>
      {steps.map((step, idx) => (
        <Panel
          header={`Step ${idx + 1}`}
          key={idx}
          style={{ background: 'rgba(102,126,234,.05)', borderRadius: 8 }}
        >
          <div style={{ fontFamily: 'monospace', fontSize: 13 }}>
            <div><b>Thought:</b> <ReactMarkdown>{step.thought}</ReactMarkdown></div>
            <div><b>Action:</b> {step.action}</div>
            <div><b>Action Input:</b> {step.action_input}</div>
            <div><b>Observation:</b> <ReactMarkdown>{step.observation}</ReactMarkdown></div>
          </div>
        </Panel>
      ))}
    </Collapse>
  );
};

const MessageItem: React.FC<{
  msg: Message;
  copyMessage: (content: string) => void;
}> = ({ msg, copyMessage }) => {
  const [collapsed, setCollapsed] = useState(true);
  const hasSteps = Array.isArray(msg.reasoningSteps) && msg.reasoningSteps.length > 0;

  return (
    <div style={{
      display: 'flex',
      justifyContent: msg.type === 'user' ? 'flex-end' : 'flex-start',
      marginBottom: 18,
    }}>
      {msg.type === 'assistant' && (
        <Avatar icon={<RobotOutlined />} style={{ background: '#667eea', marginRight: 12 }} />
      )}
      <div style={{
        maxWidth: '75%',
        background: msg.type === 'user'
          ? 'linear-gradient(135deg, #1890ff 0%, #67e8f9 100%)'
          : 'linear-gradient(135deg, #f5f6fa 0%, #e0e7ff 100%)',
        color: msg.type === 'user' ? '#fff' : '#333',
        borderRadius: msg.type === 'user' ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
        boxShadow: '0 2px 8px rgba(102,126,234,0.08)',
        padding: '14px 18px',
        fontSize: 15,
        position: 'relative',
        wordBreak: 'break-word',
      }}>
        {msg.type === 'assistant' ? (
          <>
            {msg.thinking && (
              <div style={{
                background: 'linear-gradient(135deg, #fff7e6 0%, #ffeaa7 100%)',
                borderRadius: 8,
                padding: 12,
                color: '#d63031',
                fontFamily: 'monospace',
                marginBottom: 10,
              }}>
                🤔 {msg.thinking}
              </div>
            )}

            {hasSteps && (
              <Button
                type="link"
                size="small"
                icon={<DownOutlined rotate={collapsed ? 0 : 180} />}
                onClick={() => setCollapsed(!collapsed)}
                style={{ padding: 0, height: 'auto', marginBottom: 6 }}
              >
                {collapsed ? '展开思考过程' : '折叠思考过程'}
              </Button>
            )}

            {!collapsed && renderReasoningSteps(msg.reasoningSteps)}

            {msg.finalAnswer && (
              <div style={{
                background: 'linear-gradient(90deg, #52c41a 0%, #1890ff 100%)',
                borderRadius: 8,
                padding: 12,
                color: '#fff',
                marginTop: 8,
              }}>
                <ReactMarkdown>{msg.finalAnswer}</ReactMarkdown>
              </div>
            )}
          </>
        ) : (
          <span>{msg.content}</span>
        )}

        <Button
          type="text"
          size="small"
          icon={<CopyOutlined />}
          onClick={() => copyMessage(msg.type === 'assistant' ? (msg.finalAnswer || '') : msg.content)}
          style={{
            position: 'absolute',
            top: 6,
            right: 6,
            color: msg.type === 'user' ? '#fff' : '#667eea',
            background: 'rgba(255,255,255,0.15)',
            borderRadius: '50%'
          }}
        />
      </div>
      {msg.type === 'user' && (
        <Avatar icon={<UserOutlined />} style={{ background: '#1890ff', marginLeft: 12 }} />
      )}
    </div>
  );
};

export default MessageItem; 
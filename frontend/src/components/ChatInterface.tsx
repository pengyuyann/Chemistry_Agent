import React, { useState, useRef } from 'react';
import {
  Avatar,
  Button,
  Collapse,
  Dropdown,
  Input,
  Menu,
  Spin,
  Tag,
  Typography,
  message as antdMessage,
} from 'antd';
import {
  CopyOutlined,
  DownOutlined,
  LogoutOutlined,
  RobotOutlined,
  SendOutlined,
  UserOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';

import { streamChatMessage } from '../api/chat';
import { useAuth } from '../context/AuthContext';

const { TextArea } = Input;
const { Text } = Typography;
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
          <div className="font-mono text-sm">
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
    <div className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      {msg.type === 'assistant' && (
        <Avatar icon={<RobotOutlined />} className="bg-indigo-500 mr-3" />
      )}
      <div
        className={`relative p-4 shadow-md max-w-[75%] whitespace-pre-wrap break-words rounded-xl ${
          msg.type === 'user'
            ? 'bg-gradient-to-br from-blue-500 to-cyan-300 text-white rounded-br-md'
            : 'bg-gradient-to-br from-gray-100 to-indigo-100 text-gray-800 rounded-bl-md'
        }`}
      >
        {msg.type === 'assistant' ? (
          <>
            {msg.thinking && (
              <div className="bg-gradient-to-br from-yellow-100 to-yellow-200 text-red-600 p-3 mb-2 rounded font-mono">
                🤔 {msg.thinking}
              </div>
            )}

            {hasSteps && (
              <Button
                type="link"
                size="small"
                icon={<DownOutlined rotate={collapsed ? 0 : 180} />}
                onClick={() => setCollapsed(!collapsed)}
                className="mb-1 p-0 h-auto"
              >
                {collapsed ? '展开思考过程' : '折叠思考过程'}
              </Button>
            )}

            {!collapsed && renderReasoningSteps(msg.reasoningSteps)}

            {msg.finalAnswer && (
              <div className="bg-gradient-to-r from-green-500 to-blue-500 text-white p-3 rounded mt-2">
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
          onClick={() => copyMessage(msg.type === 'assistant' ? msg.finalAnswer || '' : msg.content)}
          className="absolute top-1 right-1 text-white bg-white/20 rounded-full"
        />
      </div>
      {msg.type === 'user' && (
        <Avatar icon={<UserOutlined />} className="bg-blue-500 ml-3" />
      )}
    </div>
  );
};

export default MessageItem;

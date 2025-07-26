import React, { useState, useMemo } from 'react';
import {
  Avatar,
  Button,
  Collapse,
  Tag,
  Tooltip,
  Space,
  Typography,
} from 'antd';
import {
  CopyOutlined,
  DownOutlined,
  RobotOutlined,
  UserOutlined,
  ExperimentOutlined,
  SafetyOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import ChemicalViewer from './ChemicalViewer';

const { Panel } = Collapse;
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
  content: string;
  timestamp: Date;
  model?: string;
  reasoningSteps?: ReasoningStep[];
  finalAnswer?: string;
  thinking?: string;
}

// SMILES正则表达式
const SMILES_REGEX = /([A-Z][a-z]?|[0-9]+|[()\[\]{}@%+=#$:;\\/|~!&?<>{}"`'*\-])+/g;

// 检测文本中的SMILES
const extractSMILES = (text: string): string[] => {
  const matches = text.match(SMILES_REGEX);
  if (!matches) return [];
  
  // 过滤掉明显不是SMILES的匹配项
  return matches.filter(match => {
    // 基本的SMILES验证
    const hasValidChars = /^[A-Za-z0-9()[\]{}@%+=#$:;\\/|~!&?<>"`'*\-]+$/.test(match);
    const hasReasonableLength = match.length >= 3 && match.length <= 200;
    const hasChemicalElements = /[CHNOPSFIBrCl]/i.test(match);
    
    return hasValidChars && hasReasonableLength && hasChemicalElements;
  });
};

// 检测化学反应
const extractReactions = (text: string): string[] => {
  const reactionRegex = /([A-Z][a-z]?[0-9]*[A-Za-z0-9]*\s*\+\s*[A-Z][a-z]?[0-9]*[A-Za-z0-9]*\s*->\s*[A-Z][a-z]?[0-9]*[A-Za-z0-9]*)/g;
  return text.match(reactionRegex) || [];
};

// 渲染化学内容
const renderChemicalContent = (content: string) => {
  const smiles = extractSMILES(content);
  const reactions = extractReactions(content);
  
  return (
    <div>
      <ReactMarkdown>{content}</ReactMarkdown>
      
      {smiles.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Text strong style={{ color: '#1890ff' }}>
            <ExperimentOutlined /> 检测到的分子结构:
          </Text>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 8 }}>
            {smiles.map((smile, index) => (
              <ChemicalViewer 
                key={index}
                smiles={smile}
                width={150}
                height={100}
                title={`SMILES: ${smile}`}
              />
            ))}
          </div>
        </div>
      )}
      
      {reactions.length > 0 && (
        <div style={{ marginTop: 12 }}>
          <Text strong style={{ color: '#52c41a' }}>
            <SearchOutlined /> 检测到的化学反应:
          </Text>
          <div style={{ marginTop: 8 }}>
            {reactions.map((reaction, index) => (
              <Tag key={index} color="green" style={{ marginBottom: 4 }}>
                {reaction}
              </Tag>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

const renderReasoningSteps = (steps?: ReasoningStep[]) => {
  if (!steps?.length) return null;
  
  return (
    <Collapse ghost>
      {steps.map((step, idx) => (
        <Panel
          header={
            <Space>
              <Text strong>步骤 {idx + 1}</Text>
              {step.action && (
                <Tag color="blue" icon={<ExperimentOutlined />}>
                  {step.action}
                </Tag>
              )}
            </Space>
          }
          key={idx}
          style={{ 
            background: 'rgba(102,126,234,.05)', 
            borderRadius: 8,
            marginBottom: 8
          }}
        >
          <div style={{ fontFamily: 'monospace', fontSize: 13 }}>
            <div style={{ marginBottom: 8 }}>
              <Text strong style={{ color: '#1890ff' }}>思考过程:</Text>
              <div style={{ marginTop: 4 }}>
                <ReactMarkdown>{step.thought}</ReactMarkdown>
              </div>
            </div>
            
            <div style={{ marginBottom: 8 }}>
              <Text strong style={{ color: '#52c41a' }}>执行动作:</Text>
              <div style={{ marginTop: 4, color: '#666' }}>
                {step.action}
              </div>
            </div>
            
            <div style={{ marginBottom: 8 }}>
              <Text strong style={{ color: '#fa8c16' }}>输入参数:</Text>
              <div style={{ marginTop: 4, color: '#666' }}>
                {step.action_input}
              </div>
            </div>
            
            <div>
              <Text strong style={{ color: '#722ed1' }}>观察结果:</Text>
              <div style={{ marginTop: 4 }}>
                <ReactMarkdown>{step.observation}</ReactMarkdown>
              </div>
            </div>
          </div>
        </Panel>
      ))}
    </Collapse>
  );
};

const EnhancedMessageItem: React.FC<{
  msg: Message;
  copyMessage: (content: string) => void;
}> = ({ msg, copyMessage }) => {
  const [collapsed, setCollapsed] = useState(true);
  const hasSteps = Array.isArray(msg.reasoningSteps) && msg.reasoningSteps.length > 0;
  
  // 检测消息中的化学内容
  const hasChemicalContent = useMemo(() => {
    const content = msg.finalAnswer || msg.content;
    return extractSMILES(content).length > 0 || extractReactions(content).length > 0;
  }, [msg.finalAnswer, msg.content]);

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
                {renderChemicalContent(msg.finalAnswer)}
              </div>
            )}
            
            {hasChemicalContent && (
              <div style={{ marginTop: 8 }}>
                <Tag color="purple" icon={<SafetyOutlined />}>
                  化学内容已检测
                </Tag>
              </div>
            )}
          </>
        ) : (
          <span>{msg.content}</span>
        )}

        <Tooltip title="复制内容">
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
        </Tooltip>
      </div>
      {msg.type === 'user' && (
        <Avatar icon={<UserOutlined />} style={{ background: '#1890ff', marginLeft: 12 }} />
      )}
    </div>
  );
};

export default EnhancedMessageItem; 
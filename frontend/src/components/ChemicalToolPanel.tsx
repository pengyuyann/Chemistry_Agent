import React, { useState } from 'react';
import {
  Card,
  Button,
  Input,
  Space,
  Typography,
  Modal,
  message,
  Divider,
  Tooltip,
  Tag,
} from 'antd';
import {
  ExperimentOutlined,
  SearchOutlined,
  SafetyOutlined,
  CalculatorOutlined,
  FileTextOutlined,
  QuestionCircleOutlined,
  PlusOutlined,
  MinusOutlined,
} from '@ant-design/icons';
import ChemicalViewer from './ChemicalViewer';

const { TextArea } = Input;
const { Title, Text } = Typography;

interface ChemicalToolPanelProps {
  onToolUse?: (tool: string, input: string) => void;
}

const ChemicalToolPanel: React.FC<ChemicalToolPanelProps> = ({ onToolUse }) => {
  const [smilesInput, setSmilesInput] = useState('');
  const [moleculeName, setMoleculeName] = useState('');
  const [reactionInput, setReactionInput] = useState('');
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [activeTool, setActiveTool] = useState('');
  const [previewSmiles, setPreviewSmiles] = useState('');

  const tools = [
    {
      key: 'name2smiles',
      name: '分子名称转SMILES',
      icon: <SearchOutlined />,
      description: '将化学分子名称转换为SMILES表示',
      color: '#1890ff',
    },
    {
      key: 'smiles2name',
      name: 'SMILES转分子名称',
      icon: <FileTextOutlined />,
      description: '将SMILES表示转换为化学分子名称',
      color: '#52c41a',
    },
    {
      key: 'molecular_weight',
      name: '分子量计算',
      icon: <CalculatorOutlined />,
      description: '计算分子的分子量',
      color: '#fa8c16',
    },
    {
      key: 'safety_check',
      name: '安全性检查',
      icon: <SafetyOutlined />,
      description: '检查分子的安全性和毒性',
      color: '#f5222d',
    },
    {
      key: 'reaction_predict',
      name: '反应预测',
      icon: <ExperimentOutlined />,
      description: '预测化学反应产物',
      color: '#722ed1',
    },
    {
      key: 'retrosynthesis',
      name: '逆合成分析',
      icon: <MinusOutlined />,
      description: '分析分子的合成路径',
      color: '#13c2c2',
    },
  ];

  const handleToolClick = (toolKey: string) => {
    setActiveTool(toolKey);
    setIsModalVisible(true);
  };

  const handleToolSubmit = () => {
    let input = '';
    switch (activeTool) {
      case 'name2smiles':
        input = moleculeName;
        break;
      case 'smiles2name':
      case 'molecular_weight':
      case 'safety_check':
        input = smilesInput;
        break;
      case 'reaction_predict':
      case 'retrosynthesis':
        input = reactionInput;
        break;
    }

    if (!input.trim()) {
      message.error('请输入必要的信息');
      return;
    }

    if (onToolUse) {
      onToolUse(activeTool, input);
    }
    
    setIsModalVisible(false);
    message.success('工具已添加到对话中');
  };

  const renderToolModal = () => {
    const tool = tools.find(t => t.key === activeTool);
    if (!tool) return null;

    return (
      <Modal
        title={
          <Space>
            <span style={{ color: tool.color }}>{tool.icon}</span>
            {tool.name}
          </Space>
        }
        open={isModalVisible}
        onOk={handleToolSubmit}
        onCancel={() => setIsModalVisible(false)}
        okText="添加到对话"
        cancelText="取消"
        width={600}
      >
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">{tool.description}</Text>
        </div>
        
        {activeTool === 'name2smiles' && (
          <div>
            <Text strong>分子名称:</Text>
            <Input
              placeholder="例如: 苯酚, 乙醇, 甲苯"
              value={moleculeName}
              onChange={(e) => setMoleculeName(e.target.value)}
              style={{ marginTop: 8 }}
            />
          </div>
        )}
        
        {(activeTool === 'smiles2name' || activeTool === 'molecular_weight' || activeTool === 'safety_check') && (
          <div>
            <Text strong>SMILES:</Text>
            <Input
              placeholder="例如: CCO, c1ccccc1, CC(=O)O"
              value={smilesInput}
              onChange={(e) => {
                setSmilesInput(e.target.value);
                setPreviewSmiles(e.target.value);
              }}
              style={{ marginTop: 8 }}
            />
            {previewSmiles && (
              <div style={{ marginTop: 12 }}>
                <Text type="secondary">分子结构预览:</Text>
                <ChemicalViewer 
                  smiles={previewSmiles}
                  width={200}
                  height={120}
                  title="预览"
                />
              </div>
            )}
          </div>
        )}
        
        {(activeTool === 'reaction_predict' || activeTool === 'retrosynthesis') && (
          <div>
            <Text strong>反应SMILES或分子:</Text>
            <TextArea
              placeholder="例如: CCO + O=C=O >> CC(=O)OC, 或输入分子名称"
              value={reactionInput}
              onChange={(e) => setReactionInput(e.target.value)}
              rows={3}
              style={{ marginTop: 8 }}
            />
          </div>
        )}
      </Modal>
    );
  };

  return (
    <Card 
      title={
        <Space>
          <ExperimentOutlined style={{ color: '#1890ff' }} />
          <span>化学工具</span>
        </Space>
      }
      size="small"
      style={{ marginBottom: 16 }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 12 }}>
        {tools.map((tool) => (
          <Tooltip key={tool.key} title={tool.description}>
            <Button
              type="default"
              icon={tool.icon}
              onClick={() => handleToolClick(tool.key)}
              style={{
                height: 'auto',
                padding: '12px',
                textAlign: 'left',
                borderColor: tool.color,
                color: tool.color,
              }}
              block
            >
              <div>
                <div style={{ fontWeight: 'bold', marginBottom: 4 }}>
                  {tool.name}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {tool.description}
                </div>
              </div>
            </Button>
          </Tooltip>
        ))}
      </div>
      
      <Divider style={{ margin: '16px 0' }} />
      
      <div style={{ textAlign: 'center' }}>
        <Text type="secondary" style={{ fontSize: '12px' }}>
          <QuestionCircleOutlined /> 点击工具按钮将其添加到对话中，AI助手将使用相应的化学工具为您分析
        </Text>
      </div>
      
      {renderToolModal()}
    </Card>
  );
};

export default ChemicalToolPanel; 
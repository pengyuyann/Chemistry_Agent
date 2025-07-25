import React, { useState, useEffect } from 'react';
import { 
  Card, 
  List, 
  Typography, 
  Tag, 
  Button, 
  Space, 
  Divider,
  Spin,
  message,
  Collapse
} from 'antd';
import { 
  ToolOutlined, 
  ExperimentOutlined,
  SafetyOutlined,
  SearchOutlined,
  CalculatorOutlined,
  BookOutlined,
  ApiOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';

import apiService, { ToolCategory, ApiInfo } from '../services/api';

const { Title, Text } = Typography;
const { Panel } = Collapse;

interface SidebarProps {}

const Sidebar: React.FC<SidebarProps> = () => {
  const [tools, setTools] = useState<ToolCategory>({});
  const [apiInfo, setApiInfo] = useState<ApiInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [healthStatus, setHealthStatus] = useState<'healthy' | 'unhealthy' | 'unknown'>('unknown');

  useEffect(() => {
    loadSidebarData();
  }, []);

  const loadSidebarData = async () => {
    try {
      setLoading(true);
      
      // 并行加载数据
      const [toolsResponse, apiInfoResponse, healthResponse] = await Promise.allSettled([
        apiService.getAvailableTools(),
        apiService.getApiInfo(),
        apiService.getChemAgentHealth()
      ]);

      if (toolsResponse.status === 'fulfilled') {
        setTools(toolsResponse.value.data);
      }

      if (apiInfoResponse.status === 'fulfilled') {
        setApiInfo(apiInfoResponse.value.data);
      }

      if (healthResponse.status === 'fulfilled') {
        setHealthStatus('healthy');
      } else {
        setHealthStatus('unhealthy');
      }

    } catch (error) {
      console.error('加载侧边栏数据失败:', error);
      message.error('加载工具信息失败');
      setHealthStatus('unhealthy');
    } finally {
      setLoading(false);
    }
  };

  const getToolIcon = (toolName: string) => {
    const iconMap: Record<string, React.ReactNode> = {
      'molecular_weight': <CalculatorOutlined />,
      'molecular_formula': <CalculatorOutlined />,
      'smiles_to_iupac': <BookOutlined />,
      'iupac_to_smiles': <BookOutlined />,
      'molecular_similarity': <SearchOutlined />,
      'safety_summary': <SafetyOutlined />,
      'controlled_substance_check': <SafetyOutlined />,
      'literature_search': <SearchOutlined />,
      'reaction_planner': <ExperimentOutlined />,
      'molecule_price': <ApiOutlined />,
      'molecule_data': <ApiOutlined />,
    };
    return iconMap[toolName] || <ToolOutlined />;
  };

  const getToolColor = (toolName: string) => {
    const colorMap: Record<string, string> = {
      'molecular_weight': 'blue',
      'molecular_formula': 'blue',
      'smiles_to_iupac': 'green',
      'iupac_to_smiles': 'green',
      'molecular_similarity': 'purple',
      'safety_summary': 'red',
      'controlled_substance_check': 'red',
      'literature_search': 'orange',
      'reaction_planner': 'cyan',
      'molecule_price': 'gold',
      'molecule_data': 'gold',
    };
    return colorMap[toolName] || 'default';
  };

  const getToolDescription = (toolName: string) => {
    const descMap: Record<string, string> = {
      'molecular_weight': '计算分子量',
      'molecular_formula': '获取分子式',
      'smiles_to_iupac': 'SMILES转IUPAC名称',
      'iupac_to_smiles': 'IUPAC名称转SMILES',
      'molecular_similarity': '计算分子相似性',
      'safety_summary': '生成安全摘要',
      'controlled_substance_check': '管制物质检查',
      'literature_search': '文献搜索',
      'reaction_planner': '反应规划',
      'molecule_price': '查询分子价格',
      'molecule_data': '获取分子数据',
    };
    return descMap[toolName] || '未知工具';
  };

  const quickActions = [
    {
      title: '计算分子量',
      description: '输入分子式或SMILES',
      example: 'C6H6',
      icon: <CalculatorOutlined />
    },
    {
      title: '安全性检查',
      description: '检查化学物质安全性',
      example: 'ethanol',
      icon: <SafetyOutlined />
    },
    {
      title: '文献搜索',
      description: '搜索相关化学文献',
      example: 'benzene synthesis',
      icon: <SearchOutlined />
    },
    {
      title: '反应规划',
      description: '规划化学反应路径',
      example: 'benzene to phenol',
      icon: <ExperimentOutlined />
    }
  ];

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <Spin size="large" />
        <Text style={{ color: 'white', marginTop: '12px', display: 'block' }}>
          加载中...
        </Text>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px', height: '100%', overflow: 'auto' }}>
      {/* 状态指示器 */}
      <Card
        size="small"
        style={{
          marginBottom: '20px',
          borderRadius: '16px'
        }}
        className="slide-in-left"
      >
        <Space align="center">
          {healthStatus === 'healthy' ? (
            <CheckCircleOutlined style={{ color: '#52c41a', fontSize: '16px' }} />
          ) : (
            <ExclamationCircleOutlined style={{ color: '#ff4d4f', fontSize: '16px' }} />
          )}
          <Text style={{ color: 'white', fontSize: '14px' }}>
            服务状态: {healthStatus === 'healthy' ? '正常' : '异常'}
          </Text>
        </Space>
        {apiInfo && (
          <div style={{ marginTop: '8px' }}>
            <Text type="secondary" style={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '12px' }}>
              版本: {apiInfo.version}
            </Text>
          </div>
        )}
      </Card>

      {/* 快速操作 */}
      <Title level={5} style={{ 
        color: 'white', 
        marginBottom: '16px',
        fontSize: '18px',
        fontWeight: 'bold',
        textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
      }}>
        🚀 快速操作
      </Title>
      <List
        size="small"
        dataSource={quickActions}
        renderItem={(action) => (
          <List.Item
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              marginBottom: '8px',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              cursor: 'pointer',
              transition: 'all 0.3s ease'
            }}
            className="slide-in-left"
          >
            <List.Item.Meta
              avatar={
                <div style={{ color: 'white', fontSize: '16px' }}>
                  {action.icon}
                </div>
              }
              title={
                <Text style={{ color: 'white', fontSize: '14px', fontWeight: 'bold' }}>
                  {action.title}
                </Text>
              }
              description={
                <div>
                  <Text type="secondary" style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: '12px' }}>
                    {action.description}
                  </Text>
                  <div style={{ marginTop: '4px' }}>
                    <Tag style={{ background: 'rgba(255, 255, 255, 0.1)', color: 'white' }}>
                      示例: {action.example}
                    </Tag>
                  </div>
                </div>
              }
            />
          </List.Item>
        )}
      />

      <Divider style={{ borderColor: 'rgba(255, 255, 255, 0.1)', margin: '16px 0' }} />

      {/* 可用工具 */}
      <Title level={5} style={{ 
        color: 'white', 
        marginBottom: '16px',
        fontSize: '18px',
        fontWeight: 'bold',
        textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)'
      }}>
        🛠️ 可用工具
      </Title>
      <Collapse
        ghost
        size="small"
        style={{ background: 'transparent' }}
      >
        {Object.entries(tools).map(([category, toolList]) => (
          <Panel
            key={category}
            header={
              <Text style={{ color: 'white', fontWeight: 'bold' }}>
                {category === 'molecular_properties' ? '分子性质' :
                 category === 'safety_tools' ? '安全工具' :
                 category === 'search_tools' ? '搜索工具' :
                 category === 'reaction_tools' ? '反应工具' :
                 category === 'external_apis' ? '外部API' : category}
              </Text>
            }
            style={{ background: 'transparent' }}
          >
            <List
              size="small"
              dataSource={toolList}
              renderItem={(tool) => (
                <List.Item
                  style={{
                    padding: '12px',
                    border: 'none',
                    borderRadius: '8px',
                    marginBottom: '4px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    transition: 'all 0.3s ease'
                  }}
                  className="slide-in-left"
                >
                  <Space>
                    <div style={{ color: 'white' }}>
                      {getToolIcon(tool)}
                    </div>
                    <div>
                      <Text style={{ color: 'white', fontSize: '12px' }}>
                        {getToolDescription(tool)}
                      </Text>
                      <div style={{ marginTop: '2px' }}>
                        <Tag 
                          color={getToolColor(tool)} 
                          style={{ fontSize: '10px' }}
                        >
                          {tool}
                        </Tag>
                      </div>
                    </div>
                  </Space>
                </List.Item>
              )}
            />
          </Panel>
        ))}
      </Collapse>

      {/* 刷新按钮 */}
      <div style={{ marginTop: '24px', textAlign: 'center' }}>
        <Button
          type="text"
          size="small"
          onClick={loadSidebarData}
          icon={<ReloadOutlined />}
          style={{
            color: 'rgba(255, 255, 255, 0.7)',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            borderRadius: '12px',
            padding: '8px 16px',
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            transition: 'all 0.3s ease'
          }}
          className="slide-in-left"
        >
          刷新工具列表
        </Button>
      </div>
    </div>
  );
};

export default Sidebar; 
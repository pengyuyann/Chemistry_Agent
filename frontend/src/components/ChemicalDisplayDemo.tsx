import React, { useState } from 'react';
import { Card, Input, Space, Typography, Divider } from 'antd';
import ChemicalDisplay from './ChemicalDisplay';
import ReactionDisplay from './ReactionDisplay';
import ChemicalContentParser from './ChemicalContentParser';

const { Title, Text } = Typography;
const { TextArea } = Input;

const ChemicalDisplayDemo: React.FC = () => {
  const [smilesInput, setSmilesInput] = useState('');
  const [reactionInput, setReactionInput] = useState('');
  const [textInput, setTextInput] = useState('');

  // 示例数据
  const exampleMolecules = [
    { name: '苯', smiles: 'c1ccccc1' },
    { name: '乙醇', smiles: 'CCO' },
    { name: '咖啡因', smiles: 'CN1C=NC2=C1C(=O)N(C(=O)N2C)C' },
    { name: '阿司匹林', smiles: 'CC(=O)OC1=CC=CC=C1C(=O)O' }
  ];

  const exampleReactions = [
    {
      name: '酯化反应',
      smiles: 'CCO.CC(=O)O>>CC(=O)OCC.O'
    },
    {
      name: '加氢反应',
      smiles: 'C=C>>CC'
    }
  ];

  const exampleTexts = [
    '苯的SMILES表示为 c1ccccc1，它是一个芳香族化合物。',
    '乙醇 CCO 可以与乙酸 CC(=O)O 发生酯化反应：CCO.CC(=O)O>>CC(=O)OCC.O',
    '咖啡因的分子式为 CN1C=NC2=C1C(=O)N(C(=O)N2C)C，是一种常见的生物碱。'
  ];

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: 32 }}>
        🧪 化学显示功能演示
      </Title>

      {/* 分子结构显示 */}
      <Card title="分子结构显示" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>输入SMILES字符串：</Text>
            <Input
              value={smilesInput}
              onChange={(e) => setSmilesInput(e.target.value)}
              placeholder="例如：c1ccccc1 (苯)"
              style={{ marginTop: 8 }}
            />
          </div>
          
          {smilesInput && (
            <ChemicalDisplay
              smiles={smilesInput}
              title="输入的分子结构"
              width={300}
              height={200}
            />
          )}

          <Divider />
          
          <div>
            <Text strong>示例分子：</Text>
            <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 16 }}>
              {exampleMolecules.map((mol, index) => (
                <div key={index} style={{ flex: '0 0 calc(50% - 8px)' }}>
                  <ChemicalDisplay
                    smiles={mol.smiles}
                    title={mol.name}
                    width={250}
                    height={180}
                  />
                </div>
              ))}
            </div>
          </div>
        </Space>
      </Card>

      {/* 化学反应显示 */}
      <Card title="化学反应显示" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>输入反应SMILES：</Text>
            <Input
              value={reactionInput}
              onChange={(e) => setReactionInput(e.target.value)}
              placeholder="例如：CCO.CC(=O)O>>CC(=O)OCC.O (酯化反应)"
              style={{ marginTop: 8 }}
            />
          </div>
          
          {reactionInput && (
            <ReactionDisplay
              reactionSmiles={reactionInput}
              title="输入的化学反应"
            />
          )}

          <Divider />
          
          <div>
            <Text strong>示例反应：</Text>
            <div style={{ marginTop: 12 }}>
              {exampleReactions.map((rxn, index) => (
                <div key={index} style={{ marginBottom: 16 }}>
                  <ReactionDisplay
                    reactionSmiles={rxn.smiles}
                    title={rxn.name}
                  />
                </div>
              ))}
            </div>
          </div>
        </Space>
      </Card>

      {/* 智能文本解析 */}
      <Card title="智能文本解析" style={{ marginBottom: 24 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>输入包含化学结构的文本：</Text>
            <TextArea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder="输入包含SMILES字符串的文本，系统会自动识别并显示化学结构"
              rows={3}
              style={{ marginTop: 8 }}
            />
          </div>
          
          {textInput && (
            <Card size="small" title="解析结果" style={{ background: '#f8fafc' }}>
              <ChemicalContentParser content={textInput} />
            </Card>
          )}

          <Divider />
          
          <div>
            <Text strong>示例文本：</Text>
            <div style={{ marginTop: 12 }}>
              {exampleTexts.map((text, index) => (
                <Card 
                  key={index} 
                  size="small" 
                  title={`示例 ${index + 1}`}
                  style={{ marginBottom: 12 }}
                >
                  <ChemicalContentParser content={text} />
                </Card>
              ))}
            </div>
          </div>
        </Space>
      </Card>

      {/* 使用说明 */}
      <Card title="使用说明" size="small">
        <Space direction="vertical">
          <Text>• <strong>分子结构显示：</strong>输入有效的SMILES字符串，系统会自动生成2D分子结构图</Text>
          <Text>• <strong>化学反应显示：</strong>输入反应SMILES（格式：反应物&gt;&gt;产物），系统会显示完整的反应式</Text>
          <Text>• <strong>智能文本解析：</strong>在普通文本中包含SMILES字符串，系统会自动识别并显示相应的化学结构</Text>
          <Text>• <strong>在聊天中使用：</strong>当AI助手回答包含化学结构时，会自动显示相应的分子图像</Text>
        </Space>
      </Card>
    </div>
  );
};

export default ChemicalDisplayDemo;
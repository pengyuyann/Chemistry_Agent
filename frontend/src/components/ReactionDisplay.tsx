import React from 'react';
import { Card, Row, Col } from 'antd';
import ChemicalDisplay from './ChemicalDisplay';

interface ReactionDisplayProps {
  reactionSmiles: string;
  title?: string;
  style?: React.CSSProperties;
}

const ReactionDisplay: React.FC<ReactionDisplayProps> = ({
  reactionSmiles,
  title = "化学反应",
  style
}) => {
  // 解析反应SMILES，分离反应物和产物
  const parseReactionSmiles = (rxnSmiles: string) => {
    if (!rxnSmiles || !rxnSmiles.includes('>')) {
      return { reactants: [], products: [] };
    }

    const parts = rxnSmiles.split('>');
    if (parts.length < 2) {
      return { reactants: [], products: [] };
    }

    const reactants = parts[0].split('.').filter(s => s.trim() !== '');
    const products = parts[parts.length - 1].split('.').filter(s => s.trim() !== '');

    return { reactants, products };
  };

  const { reactants, products } = parseReactionSmiles(reactionSmiles);

  if (reactants.length === 0 && products.length === 0) {
    return null;
  }

  return (
    <Card
      title={title}
      size="small"
      style={{
        marginBottom: 16,
        ...style
      }}
      styles={{
        body: {
          padding: 16
        }
      }}
    >
      <Row gutter={[16, 16]} align="middle">
        {/* 反应物 */}
        <Col span={10}>
          <div style={{ textAlign: 'center', marginBottom: 12 }}>
            <div style={{
              fontSize: 14,
              fontWeight: 600,
              color: '#1e293b',
              marginBottom: 8
            }}>
              反应物
            </div>
            {reactants.map((smiles, index) => (
              <div key={index} style={{ marginBottom: 8 }}>
                <ChemicalDisplay
                  smiles={smiles}
                  width={200}
                  height={150}
                  style={{ margin: '0 auto' }}
                />
                {index < reactants.length - 1 && (
                  <div style={{
                    textAlign: 'center',
                    fontSize: 18,
                    color: '#667eea',
                    fontWeight: 'bold',
                    margin: '8px 0'
                  }}>
                    +
                  </div>
                )}
              </div>
            ))}
          </div>
        </Col>

        {/* 反应箭头 */}
        <Col span={4}>
          <div style={{
            textAlign: 'center',
            fontSize: 24,
            color: '#667eea',
            fontWeight: 'bold'
          }}>
            →
          </div>
        </Col>

        {/* 产物 */}
        <Col span={10}>
          <div style={{ textAlign: 'center', marginBottom: 12 }}>
            <div style={{
              fontSize: 14,
              fontWeight: 600,
              color: '#1e293b',
              marginBottom: 8
            }}>
              产物
            </div>
            {products.map((smiles, index) => (
              <div key={index} style={{ marginBottom: 8 }}>
                <ChemicalDisplay
                  smiles={smiles}
                  width={200}
                  height={150}
                  style={{ margin: '0 auto' }}
                />
                {index < products.length - 1 && (
                  <div style={{
                    textAlign: 'center',
                    fontSize: 18,
                    color: '#667eea',
                    fontWeight: 'bold',
                    margin: '8px 0'
                  }}>
                    +
                  </div>
                )}
              </div>
            ))}
          </div>
        </Col>
      </Row>

      {/* 显示完整的反应SMILES */}
      <div style={{
        marginTop: 16,
        padding: 12,
        background: '#f8fafc',
        borderRadius: 8,
        border: '1px solid #e2e8f0'
      }}>
        <div style={{
          fontSize: 12,
          color: '#64748b',
          marginBottom: 4,
          fontWeight: 500
        }}>
          反应SMILES:
        </div>
        <div style={{
          fontSize: 12,
          color: '#1e293b',
          fontFamily: 'monospace',
          wordBreak: 'break-all'
        }}>
          {reactionSmiles}
        </div>
      </div>
    </Card>
  );
};

export default ReactionDisplay;
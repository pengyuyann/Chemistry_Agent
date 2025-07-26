import React, { useState, useEffect } from 'react';
import { Card, Spin, Alert, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

interface ChemicalViewerProps {
  smiles: string;
  width?: number;
  height?: number;
  title?: string;
}

const ChemicalViewer: React.FC<ChemicalViewerProps> = ({
  smiles,
  width = 200,
  height = 120,
  title = '分子结构'
}) => {
  const [svgContent, setSvgContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>('');

  const fetchMoleculeSVG = async (smilesString: string) => {
    if (!smilesString) return;
    
    setLoading(true);
    setError('');
    
    try {
      const url = "https://www.simolecule.com/cdkdepict/depict/wob/svg";
      const params = new URLSearchParams({
        smi: smilesString,
        annotate: "colmap",
        zoom: "2",
        w: width.toString(),
        h: height.toString(),
        abbr: "off",
      });

      const response = await fetch(`${url}?${params}`);
      
      if (!response.ok) {
        throw new Error('无法获取分子结构图');
      }
      
      const svgText = await response.text();
      setSvgContent(svgText);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取分子结构失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMoleculeSVG(smiles);
  }, [smiles, width, height]);

  const handleRefresh = () => {
    fetchMoleculeSVG(smiles);
  };

  return (
    <Card 
      title={title} 
      size="small"
      style={{ width: width + 20, margin: '8px 0' }}
      extra={
        <Button 
          type="text" 
          size="small" 
          icon={<ReloadOutlined />} 
          onClick={handleRefresh}
          loading={loading}
        />
      }
    >
      <div style={{ textAlign: 'center', minHeight: height }}>
        {loading && <Spin size="small" />}
        {error && (
          <Alert 
            message={error} 
            type="error" 
            showIcon 
            style={{ fontSize: '12px' }}
          />
        )}
        {!loading && !error && svgContent && (
          <div 
            dangerouslySetInnerHTML={{ __html: svgContent }}
            style={{ display: 'inline-block' }}
          />
        )}
      </div>
    </Card>
  );
};

export default ChemicalViewer; 
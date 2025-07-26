import React, { useState, useEffect } from 'react';
import { Spin, Alert, Card } from 'antd';

interface ChemicalDisplayProps {
  smiles: string;
  width?: number;
  height?: number;
  title?: string;
  style?: React.CSSProperties;
}

const ChemicalDisplay: React.FC<ChemicalDisplayProps> = ({
  smiles,
  width = 300,
  height = 200,
  title,
  style
}) => {
  const [imageUrl, setImageUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  // 简单的SMILES验证函数
  const isValidSMILES = (smilesString: string): boolean => {
    if (!smilesString || smilesString.trim() === '') return false;
    
    const trimmed = smilesString.trim();
    
    // 检查是否只包含无效字符
    const invalidPatterns = [
      /^#+$/, // 只有#号
      /^\d+\.$/, // 只有数字和点
      /^[^A-Za-z0-9[\]()=\-+#@/\\]+$/, // 不包含任何有效的SMILES字符
      /^[/\\]+$/, // 只有斜杠
      /^\.+$/, // 只有点
    ];
    
    // 检查是否匹配任何无效模式
    if (invalidPatterns.some(pattern => pattern.test(trimmed))) {
      return false;
    }
    
    // 检查长度（太短的字符串通常无效）
    if (trimmed.length < 1) return false;
    
    // 基本的字符检查 - SMILES应该包含至少一个字母或数字
    if (!/[A-Za-z0-9]/.test(trimmed)) return false;
    
    return true;
  };

  useEffect(() => {
    if (!smiles || smiles.trim() === '') {
      setImageUrl('');
      setError('');
      return;
    }

    const generateMoleculeImage = () => {
      const trimmedSmiles = smiles.trim();
      
      // 验证SMILES字符串
      if (!isValidSMILES(trimmedSmiles)) {
        setError('无效的SMILES字符串格式');
        setLoading(false);
        setImageUrl('');
        return;
      }
      
      setLoading(true);
      setError('');
      
      try {
        // 构建CDK Depict URL，直接作为图片源使用
        const params = new URLSearchParams({
          smi: trimmedSmiles,
          w: width.toString(),
          h: height.toString(),
          fmt: 'png', // 使用PNG格式避免SVG的CORS问题
          annotate: 'none',
          zoom: '1.0'
        });
        
        const url = `https://www.simolecule.com/cdkdepict/depict/wob/png?${params.toString()}`;
        setImageUrl(url);
        setLoading(false);
      } catch (err) {
        console.error('生成分子图像URL失败:', err);
        setError(`无法生成分子结构图: ${err instanceof Error ? err.message : '未知错误'}`);
        setLoading(false);
      }
    };

    generateMoleculeImage();
  }, [smiles, width, height]);

  const handleImageLoad = () => {
    setLoading(false);
    setError('');
  };

  const handleImageError = (event: React.SyntheticEvent<HTMLImageElement, Event>) => {
    setLoading(false);
    console.error('化学结构图片加载失败:', event);
    
    // 检查是否是网络错误或服务器错误
    const img = event.target as HTMLImageElement;
    if (img.src.includes('simolecule.com')) {
      setError('无法从CDK Depict服务加载分子结构图。可能原因：网络连接问题、SMILES字符串无效或服务暂时不可用。');
    } else {
      setError('无法加载分子结构图，请检查网络连接或SMILES字符串是否正确');
    }
  };

  if (!smiles || smiles.trim() === '') {
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
          padding: 12,
          textAlign: 'center'
        }
      }}
    >
      {loading && (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          height: height,
          width: width,
          margin: '0 auto'
        }}>
          <Spin size="large" />
        </div>
      )}

      {error && (
        <Alert
          message="显示错误"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 12 }}
        />
      )}

      {imageUrl && !error && (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 8
        }}>
          <div style={{
            border: '1px solid #e2e8f0',
            borderRadius: 8,
            padding: 8,
            background: '#ffffff',
            boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            maxWidth: '100%',
            overflow: 'hidden'
          }}>
            <img
              src={imageUrl}
              alt={`分子结构: ${smiles}`}
              style={{
                maxWidth: '100%',
                height: 'auto',
                display: loading ? 'none' : 'block'
              }}
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
          </div>
          <div style={{
            fontSize: 12,
            color: '#64748b',
            fontFamily: 'monospace',
            background: '#f8fafc',
            padding: '4px 8px',
            borderRadius: 4,
            border: '1px solid #e2e8f0',
            wordBreak: 'break-all',
            maxWidth: '100%'
          }}>
            SMILES: {smiles}
          </div>
        </div>
      )}
    </Card>
  );
};

export default ChemicalDisplay;
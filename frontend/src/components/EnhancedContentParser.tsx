import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Typography, Divider } from 'antd';
import ChemicalDisplay from './ChemicalDisplay';
import ReactionDisplay from './ReactionDisplay';

const { Text, Paragraph } = Typography;

// SMILES字符串检测正则表达式
const SMILES_PATTERN = /\b[A-Za-z0-9@+\-\[\]()=#$\/\\%]{3,}\b/g;
const REACTION_SMILES_PATTERN = /[A-Za-z0-9@+\-\[\]()=#$\/\\%.]{2,}>[A-Za-z0-9@+\-\[\]()=#$\/\\%.*]*>[A-Za-z0-9@+\-\[\]()=#$\/\\%.]{2,}/g;

interface EnhancedContentParserProps {
  content: string;
  enableMarkdown?: boolean;
  enableChemicalDetection?: boolean;
}

const EnhancedContentParser: React.FC<EnhancedContentParserProps> = ({ 
  content, 
  enableMarkdown = true,
  enableChemicalDetection = true 
}) => {
  // 检测是否为有效的SMILES字符串
  const isValidSmiles = (text: string): boolean => {
    // 基本的SMILES验证规则
    if (text.length < 3 || text.length > 200) return false;
    
    // 检查是否包含SMILES常见字符
    const smilesChars = /^[A-Za-z0-9@+\-\[\]()=#$\/\\%\.]+$/;
    if (!smilesChars.test(text)) return false;
    
    // 必须包含至少一个字母
    if (!/[A-Za-z]/.test(text)) return false;
    
    // 检查括号是否匹配
    let bracketCount = 0;
    let squareBracketCount = 0;
    for (const char of text) {
      if (char === '(') bracketCount++;
      if (char === ')') bracketCount--;
      if (char === '[') squareBracketCount++;
      if (char === ']') squareBracketCount--;
      if (bracketCount < 0 || squareBracketCount < 0) return false;
    }
    
    return bracketCount === 0 && squareBracketCount === 0;
  };

  // 检测是否为反应SMILES
  const isReactionSmiles = (text: string): boolean => {
    return text.includes('>') && REACTION_SMILES_PATTERN.test(text);
  };

  // 预处理内容，提取化学结构
  const preprocessContent = (text: string): string => {
    if (!enableChemicalDetection) return text;

    let processedText = text;
    const chemicalComponents: { [key: string]: React.ReactNode } = {};
    let componentIndex = 0;

    // 处理反应SMILES
    const reactionMatches = Array.from(text.matchAll(REACTION_SMILES_PATTERN));
    for (const match of reactionMatches) {
      const placeholder = `__CHEMICAL_REACTION_${componentIndex}__`;
      chemicalComponents[placeholder] = (
        <div key={`reaction-${componentIndex}`} style={{ margin: '12px 0' }}>
          <ReactionDisplay
            reactionSmiles={match[0]}
            title="化学反应"
          />
        </div>
      );
      processedText = processedText.replace(match[0], placeholder);
      componentIndex++;
    }

    // 处理单独的SMILES
    const words = processedText.split(/\s+/);
    for (let i = 0; i < words.length; i++) {
      const word = words[i].replace(/[.,;:!?]$/, ''); // 移除末尾标点
      
      if (isValidSmiles(word) && !isReactionSmiles(word)) {
        const placeholder = `__CHEMICAL_MOLECULE_${componentIndex}__`;
        chemicalComponents[placeholder] = (
          <div key={`molecule-${componentIndex}`} style={{ margin: '12px 0' }}>
            <ChemicalDisplay
              smiles={word}
              title="分子结构"
              width={250}
              height={180}
            />
          </div>
        );
        processedText = processedText.replace(words[i], placeholder);
        componentIndex++;
      }
    }

    // 存储化学组件以供后续渲染
    (EnhancedContentParser as any).chemicalComponents = chemicalComponents;
    
    return processedText;
  };

  // 自定义Markdown组件
  const markdownComponents = {
    // 自定义段落组件
    p: ({ children }: any) => {
      const content = React.Children.toArray(children).join('');
      const chemicalComponents = (EnhancedContentParser as any).chemicalComponents || {};
      
      // 检查是否包含化学组件占位符
      const hasChemicalPlaceholder = Object.keys(chemicalComponents).some(key => 
        typeof content === 'string' && content.includes(key)
      );

      if (hasChemicalPlaceholder) {
        const parts = typeof content === 'string' ? content.split(/(__CHEMICAL_(?:REACTION|MOLECULE)_\d+__)/g) : [content];
        return (
          <div style={{ marginBottom: 16 }}>
            {parts.map((part, index) => {
              if (typeof part === 'string' && chemicalComponents[part]) {
                return chemicalComponents[part];
              }
              return part ? <span key={index}>{part}</span> : null;
            })}
          </div>
        );
      }

      return <Paragraph style={{ marginBottom: 12, lineHeight: 1.6 }}>{children}</Paragraph>;
    },

    // 自定义代码块
    code: ({ inline, className, children, ...props }: any) => {
      if (inline) {
        return (
          <Text 
            code 
            style={{ 
              background: '#f6f8fa', 
              padding: '2px 6px', 
              borderRadius: 4,
              fontSize: '0.9em'
            }}
          >
            {children}
          </Text>
        );
      }
      return (
        <pre 
          style={{ 
            background: '#f6f8fa', 
            padding: 16, 
            borderRadius: 8, 
            overflow: 'auto',
            border: '1px solid #e1e4e8',
            marginBottom: 16
          }}
        >
          <code className={className} {...props}>
            {children}
          </code>
        </pre>
      );
    },

    // 自定义标题
    h1: ({ children }: any) => (
      <Typography.Title level={2} style={{ marginTop: 24, marginBottom: 16 }}>
        {children}
      </Typography.Title>
    ),
    h2: ({ children }: any) => (
      <Typography.Title level={3} style={{ marginTop: 20, marginBottom: 12 }}>
        {children}
      </Typography.Title>
    ),
    h3: ({ children }: any) => (
      <Typography.Title level={4} style={{ marginTop: 16, marginBottom: 8 }}>
        {children}
      </Typography.Title>
    ),

    // 自定义列表
    ul: ({ children }: any) => (
      <ul style={{ marginBottom: 16, paddingLeft: 24 }}>{children}</ul>
    ),
    ol: ({ children }: any) => (
      <ol style={{ marginBottom: 16, paddingLeft: 24 }}>{children}</ol>
    ),
    li: ({ children }: any) => (
      <li style={{ marginBottom: 4, lineHeight: 1.6 }}>{children}</li>
    ),

    // 自定义分割线
    hr: () => <Divider style={{ margin: '24px 0' }} />,

    // 自定义表格
    table: ({ children }: any) => (
      <div style={{ overflowX: 'auto', marginBottom: 16 }}>
        <table style={{ 
          width: '100%', 
          borderCollapse: 'collapse',
          border: '1px solid #e1e4e8'
        }}>
          {children}
        </table>
      </div>
    ),
    th: ({ children }: any) => (
      <th style={{ 
        padding: '8px 12px', 
        background: '#f6f8fa',
        border: '1px solid #e1e4e8',
        fontWeight: 600,
        textAlign: 'left'
      }}>
        {children}
      </th>
    ),
    td: ({ children }: any) => (
      <td style={{ 
        padding: '8px 12px', 
        border: '1px solid #e1e4e8'
      }}>
        {children}
      </td>
    ),

    // 自定义引用
    blockquote: ({ children }: any) => (
      <div style={{
        borderLeft: '4px solid #dfe2e5',
        paddingLeft: 16,
        marginLeft: 0,
        marginBottom: 16,
        color: '#6a737d',
        fontStyle: 'italic'
      }}>
        {children}
      </div>
    ),
  };

  const processedContent = preprocessContent(content);

  if (!enableMarkdown) {
    // 如果不启用Markdown，直接渲染处理后的内容
    const chemicalComponents = (EnhancedContentParser as any).chemicalComponents || {};
    const parts = processedContent.split(/(__CHEMICAL_(?:REACTION|MOLECULE)_\d+__)/g);
    
    return (
      <div>
        {parts.map((part, index) => {
          if (chemicalComponents[part]) {
            return chemicalComponents[part];
          }
          return part ? <span key={index}>{part}</span> : null;
        })}
      </div>
    );
  }

  return (
    <div style={{ 
      fontSize: 15, 
      lineHeight: 1.6,
      color: '#1e293b'
    }}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={markdownComponents}
      >
        {processedContent}
      </ReactMarkdown>
    </div>
  );
};

export default EnhancedContentParser;
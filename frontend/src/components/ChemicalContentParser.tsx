import React from 'react';
import ChemicalDisplay from './ChemicalDisplay';
import ReactionDisplay from './ReactionDisplay';

// SMILES字符串检测正则表达式
const SMILES_PATTERN = /\b[A-Za-z0-9@+\-\[\]()=#$\/\\%]+\b/g;
const REACTION_SMILES_PATTERN = /[A-Za-z0-9@+\-\[\]()=#$\/\\%.]+>[A-Za-z0-9@+\-\[\]()=#$\/\\%.*]*>[A-Za-z0-9@+\-\[\]()=#$\/\\%.]+/g;

interface ChemicalContentParserProps {
  content: string;
}

const ChemicalContentParser: React.FC<ChemicalContentParserProps> = ({ content }) => {
  // 检测是否为有效的SMILES字符串
  const isValidSmiles = (text: string): boolean => {
    // 基本的SMILES验证规则
    if (text.length < 2 || text.length > 200) return false;
    
    // 检查是否包含SMILES常见字符
    const smilesChars = /^[A-Za-z0-9@+\-\[\]()=#$\/\\%\.]+$/;
    if (!smilesChars.test(text)) return false;
    
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

  // 解析内容，提取化学结构
  const parseContent = (text: string) => {
    const elements: React.ReactNode[] = [];
    let lastIndex = 0;

    // 首先查找反应SMILES
    const reactionMatches = Array.from(text.matchAll(REACTION_SMILES_PATTERN));
    
    for (const match of reactionMatches) {
      const matchStart = match.index!;
      const matchEnd = matchStart + match[0].length;
      
      // 添加匹配前的文本
      if (matchStart > lastIndex) {
        elements.push(text.substring(lastIndex, matchStart));
      }
      
      // 添加反应显示组件
      elements.push(
        <ReactionDisplay
          key={`reaction-${matchStart}`}
          reactionSmiles={match[0]}
          title="检测到的化学反应"
        />
      );
      
      lastIndex = matchEnd;
    }

    // 在剩余文本中查找单独的SMILES
    const remainingText = text.substring(lastIndex);
    const words = remainingText.split(/\s+/);
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      
      if (isValidSmiles(word) && !isReactionSmiles(word)) {
        // 添加当前累积的文本
        if (currentText) {
          elements.push(currentText + ' ');
          currentText = '';
        }
        
        // 添加分子显示组件
        elements.push(
          <ChemicalDisplay
            key={`molecule-${lastIndex}-${i}`}
            smiles={word}
            title="检测到的分子结构"
            width={250}
            height={180}
          />
        );
      } else {
        currentText += (currentText ? ' ' : '') + word;
      }
    }
    
    // 添加剩余文本
    if (currentText) {
      elements.push(currentText);
    }

    return elements;
  };

  const parsedElements = parseContent(content);

  // 如果没有检测到化学结构，返回原始内容
  if (parsedElements.length <= 1 && typeof parsedElements[0] === 'string') {
    return <span>{content}</span>;
  }

  return (
    <div>
      {parsedElements.map((element, index) => (
        <React.Fragment key={index}>
          {typeof element === 'string' ? <span>{element}</span> : element}
        </React.Fragment>
      ))}
    </div>
  );
};

export default ChemicalContentParser;
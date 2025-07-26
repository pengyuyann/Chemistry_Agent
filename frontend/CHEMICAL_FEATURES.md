# 化学智能助手前端 - 新增功能特性

## 🧪 化学分子可视化

### ChemicalViewer 组件
- **功能**: 自动检测并可视化SMILES分子结构
- **API**: 使用CDK Depict服务生成分子结构图
- **特性**: 
  - 实时预览分子结构
  - 支持多种分子格式
  - 错误处理和重试机制
  - 可自定义尺寸和标题

### 使用示例
```tsx
import ChemicalViewer from './components/ChemicalViewer';

<ChemicalViewer 
  smiles="CCO" 
  width={200} 
  height={120} 
  title="乙醇分子结构" 
/>
```

## 🔬 增强版消息组件

### EnhancedMessageItem 组件
- **功能**: 智能检测和渲染化学内容
- **特性**:
  - 自动识别SMILES分子表示
  - 检测化学反应表达式
  - 集成分子结构可视化
  - 增强的思考过程展示
  - 化学内容标签标识

### 化学内容检测
- **SMILES检测**: 使用正则表达式识别分子结构
- **反应检测**: 识别化学反应表达式
- **智能过滤**: 过滤无效的化学表示

## 🛠️ 化学工具面板

### ChemicalToolPanel 组件
- **功能**: 提供常用化学工具的快捷操作
- **工具列表**:
  1. **分子名称转SMILES**: 将化学名称转换为SMILES
  2. **SMILES转分子名称**: 将SMILES转换为化学名称
  3. **分子量计算**: 计算分子量
  4. **安全性检查**: 检查分子安全性和毒性
  5. **反应预测**: 预测化学反应产物
  6. **逆合成分析**: 分析分子合成路径

### 工具使用流程
1. 点击工具按钮
2. 在弹出的模态框中输入参数
3. 系统自动将工具请求添加到对话中
4. AI助手使用相应工具进行分析

## 🎨 增强版聊天界面

### EnhancedChatInterface 组件
- **功能**: 集成所有化学功能的完整聊天界面
- **特性**:
  - 侧边栏化学工具面板
  - 实时流式消息处理
  - 化学内容自动检测和可视化
  - 聊天记录导出功能
  - 响应式设计

### 界面布局
```
┌─────────────────┬─────────────────────────────┐
│   化学工具面板    │          聊天区域            │
│                 │                             │
│ • 分子转换工具    │  ┌─────────────────────────┐ │
│ • 计算工具       │  │      消息列表            │ │
│ • 分析工具       │  │  • 用户消息              │ │
│                 │  │  • AI回复                │ │
│ ┌─────────────┐ │  │  • 分子结构可视化        │ │
│ │ 工具快捷操作  │ │  │  • 思考过程展示          │ │
│ └─────────────┘ │  └─────────────────────────┘ │
│                 │                             │
│ ┌─────────────┐ │  ┌─────────────────────────┐ │
│ │ 聊天控制     │ │  │      输入区域            │ │
│ └─────────────┘ │  └─────────────────────────┘ │
└─────────────────┴─────────────────────────────┘
```

## 🔧 技术实现

### 分子结构可视化
```typescript
// 使用CDK Depict API
const fetchMoleculeSVG = async (smilesString: string) => {
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
  const svgText = await response.text();
  return svgText;
};
```

### SMILES检测算法
```typescript
const SMILES_REGEX = /([A-Z][a-z]?|[0-9]+|[()\[\]{}@%+=#$:;\\/|~!&?<>{}"`'*\-])+/g;

const extractSMILES = (text: string): string[] => {
  const matches = text.match(SMILES_REGEX);
  if (!matches) return [];
  
  return matches.filter(match => {
    const hasValidChars = /^[A-Za-z0-9()[\]{}@%+=#$:;\\/|~!&?<>"`'*\-]+$/.test(match);
    const hasReasonableLength = match.length >= 3 && match.length <= 200;
    const hasChemicalElements = /[CHNOPSFIBrCl]/i.test(match);
    
    return hasValidChars && hasReasonableLength && hasChemicalElements;
  });
};
```

## 🎯 使用场景

### 1. 分子结构分析
- 输入: "分析苯酚的分子结构"
- 输出: 自动显示苯酚的分子结构图和相关化学信息

### 2. 化学反应预测
- 输入: "预测乙醇和乙酸的酯化反应"
- 输出: 显示反应方程式和产物结构

### 3. 安全性评估
- 输入: "检查甲醇的安全性"
- 输出: 显示甲醇结构图和毒性分析

### 4. 分子量计算
- 输入: "计算葡萄糖的分子量"
- 输出: 显示葡萄糖结构和分子量计算结果

## 🚀 未来扩展

### 计划功能
1. **3D分子可视化**: 集成3D分子结构显示
2. **光谱分析**: 显示IR、NMR等光谱数据
3. **数据库集成**: 连接化学数据库进行查询
4. **反应路径可视化**: 显示多步反应的路径图
5. **分子性质预测**: 预测分子的物理化学性质

### 技术优化
1. **缓存机制**: 缓存常用的分子结构图
2. **离线支持**: 支持离线分子结构生成
3. **性能优化**: 优化大量分子的渲染性能
4. **移动端适配**: 优化移动设备上的显示效果

## 📝 开发指南

### 添加新的化学工具
1. 在`ChemicalToolPanel`中添加工具定义
2. 实现工具的参数输入界面
3. 在`EnhancedMessageItem`中添加相应的渲染逻辑
4. 更新API接口以支持新工具

### 自定义分子可视化
1. 修改`ChemicalViewer`组件的样式
2. 调整CDK Depict API的参数
3. 添加自定义的分子渲染逻辑

### 扩展化学内容检测
1. 更新正则表达式模式
2. 添加新的化学格式支持
3. 优化检测算法的准确性

---

*本文档描述了化学智能助手前端的化学功能特性，包括分子可视化、工具集成和用户界面优化。* 
# Chemistry Agent 前端

这是 Chemistry Agent 的 React 前端界面，提供了现代化的用户界面来与化学助手进行交互。

## 🚀 功能特性

- **现代化UI设计**: 使用 Ant Design 和 Framer Motion 构建的美观界面
- **实时聊天**: 支持与 Chemistry Agent 的实时对话
- **工具展示**: 侧边栏显示所有可用的化学工具
- **状态监控**: 实时显示后端服务状态
- **响应式设计**: 适配不同屏幕尺寸
- **代码高亮**: 支持 Markdown 和代码语法高亮

## 📦 安装依赖

```bash
npm install
```

## 🏃‍♂️ 启动开发服务器

```bash
npm start
```

前端将在 `http://localhost:3000` 启动。

## 🏗️ 构建生产版本

```bash
npm run build
```

## 🔧 配置

### 环境变量

创建 `.env` 文件来配置API地址：

```env
REACT_APP_API_URL=http://localhost:8000
```

### 代理配置

在 `package.json` 中已配置代理到后端：

```json
{
  "proxy": "http://localhost:8000"
}
```

## 📁 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── components/         # React组件
│   │   ├── ChatInterface.tsx    # 聊天界面
│   │   └── Sidebar.tsx          # 侧边栏
│   ├── services/           # API服务
│   │   └── api.ts              # API接口定义
│   ├── App.tsx             # 主应用组件
│   ├── App.css             # 应用样式
│   ├── index.tsx           # 应用入口
│   └── index.css           # 全局样式
├── package.json            # 依赖配置
├── tsconfig.json           # TypeScript配置
└── README.md               # 项目说明
```

## 🎨 技术栈

- **React 18**: 前端框架
- **TypeScript**: 类型安全
- **Ant Design**: UI组件库
- **Framer Motion**: 动画库
- **Axios**: HTTP客户端
- **React Markdown**: Markdown渲染
- **React Syntax Highlighter**: 代码高亮

## 🔌 API集成

前端通过 `src/services/api.ts` 与后端API进行通信，支持：

- 健康检查
- 获取API信息
- 获取可用工具
- 发送聊天消息

## 🎯 使用示例

1. **启动后端服务**:
   ```bash
   cd ../
   python start_server.py
   ```

2. **启动前端**:
   ```bash
   cd frontend
   npm start
   ```

3. **开始对话**:
   - 在聊天界面输入化学问题
   - 查看侧边栏的可用工具
   - 监控服务状态

## 🐛 故障排除

### 常见问题

1. **API连接失败**
   - 确保后端服务在 `http://localhost:8000` 运行
   - 检查网络连接和防火墙设置

2. **依赖安装失败**
   - 清除 npm 缓存: `npm cache clean --force`
   - 删除 node_modules 并重新安装: `rm -rf node_modules && npm install`

3. **TypeScript错误**
   - 确保安装了所有类型定义: `npm install --save-dev @types/node`

## 📝 开发指南

### 添加新组件

1. 在 `src/components/` 创建新组件
2. 使用 TypeScript 定义接口
3. 添加适当的样式和动画
4. 更新相关文档

### 修改API接口

1. 更新 `src/services/api.ts` 中的接口定义
2. 修改相关组件的API调用
3. 测试新的API功能

### 样式定制

- 全局样式在 `src/index.css`
- 组件样式在各自的CSS文件
- 使用CSS变量进行主题定制

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。 
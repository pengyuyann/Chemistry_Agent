# Chemistry Agent 前端设置指南

## 🎯 概述

本指南将帮助你设置和运行 Chemistry Agent 的前端界面。前端使用 React + TypeScript + Ant Design 构建，提供了现代化的用户界面。

## 📋 前置要求

### 1. Node.js 和 npm
- **Node.js**: 版本 16.0 或更高
- **npm**: 版本 8.0 或更高

### 2. 后端服务
确保后端服务正在运行：
```bash
python start_server.py
```

## 🚀 快速启动

### 方法一：使用启动脚本（推荐）

```bash
python start_frontend.py
```

这个脚本会自动：
- 检查 Node.js 和 npm 是否已安装
- 安装前端依赖
- 启动开发服务器

### 方法二：手动启动

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 启动开发服务器
npm start
```

## 📁 项目结构

```
Chemistry_Agent/
├── app/                    # 后端代码
├── frontend/              # 前端代码
│   ├── public/            # 静态资源
│   ├── src/
│   │   ├── components/    # React组件
│   │   │   ├── ChatInterface.tsx
│   │   │   └── Sidebar.tsx
│   │   ├── services/      # API服务
│   │   │   └── api.ts
│   │   ├── App.tsx        # 主应用
│   │   └── index.tsx      # 入口文件
│   ├── package.json       # 依赖配置
│   └── tsconfig.json      # TypeScript配置
├── start_server.py        # 后端启动脚本
├── start_frontend.py      # 前端启动脚本
└── README.md
```

## 🎨 界面特性

### 主要功能
- **聊天界面**: 与 Chemistry Agent 进行对话
- **侧边栏**: 显示可用工具和服务状态
- **实时状态**: 监控后端服务健康状态
- **工具展示**: 分类显示所有化学工具

### 设计特色
- **现代化UI**: 使用 Ant Design 组件库
- **动画效果**: Framer Motion 提供流畅动画
- **响应式设计**: 适配不同屏幕尺寸
- **代码高亮**: 支持 Markdown 和语法高亮

## 🔧 配置选项

### 环境变量
创建 `frontend/.env` 文件：
```env
REACT_APP_API_URL=http://localhost:8000
```

### 代理配置
`package.json` 中已配置代理：
```json
{
  "proxy": "http://localhost:8000"
}
```

## 🐛 常见问题

### 1. Node.js 未安装
**错误**: `'node' is not recognized`
**解决**: 
- 访问 https://nodejs.org/ 下载安装
- 或使用包管理器安装：
  ```bash
  # Windows (使用 chocolatey)
  choco install nodejs
  
  # macOS (使用 homebrew)
  brew install node
  
  # Linux (Ubuntu/Debian)
  sudo apt install nodejs npm
  ```

### 2. 依赖安装失败
**错误**: `npm ERR! code ENOENT`
**解决**:
```bash
# 清除缓存
npm cache clean --force

# 删除 node_modules 重新安装
rm -rf node_modules package-lock.json
npm install
```

### 3. 端口被占用
**错误**: `Port 3000 is already in use`
**解决**:
```bash
# 查找占用端口的进程
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# 杀死进程或使用其他端口
PORT=3001 npm start
```

### 4. API 连接失败
**错误**: `Failed to fetch`
**解决**:
- 确保后端服务在 `http://localhost:8000` 运行
- 检查防火墙设置
- 验证代理配置

## 🛠️ 开发指南

### 添加新组件
1. 在 `src/components/` 创建新文件
2. 使用 TypeScript 定义接口
3. 导入必要的依赖
4. 在 `App.tsx` 中使用组件

### 修改样式
- 全局样式: `src/index.css`
- 组件样式: 各自的 CSS 文件
- 主题定制: 修改 Ant Design 主题变量

### API 集成
- 接口定义: `src/services/api.ts`
- 类型定义: 在 `api.ts` 中定义接口类型
- 错误处理: 使用 try-catch 和用户友好的错误消息

## 📱 浏览器支持

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🔒 安全注意事项

- 前端不存储敏感信息
- API 密钥通过环境变量管理
- 使用 HTTPS 在生产环境中
- 定期更新依赖包

## 📈 性能优化

- 使用 React.memo 优化组件渲染
- 懒加载大型组件
- 压缩和优化静态资源
- 使用 CDN 加速

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📞 支持

如果遇到问题：
1. 查看本文档的常见问题部分
2. 检查控制台错误信息
3. 提交 Issue 到项目仓库

---

🎉 现在你可以享受 Chemistry Agent 的现代化前端界面了！ 
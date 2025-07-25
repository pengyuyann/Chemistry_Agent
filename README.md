# Chemistry Agent API

智能化学助手API，基于大语言模型和化学工具链，支持分子分析、合成规划、安全性检查等化学任务。

## 🚀 功能特性

- **分子分析**: 计算分子量、识别官能团、计算分子相似性
- **合成规划**: 反应产物预测、逆合成分析
- **安全性检查**: 爆炸性检查、管制化学品检查、安全性总结
- **信息检索**: 网络搜索、学术文献搜索、专利检查
- **化学结构转换**: SMILES格式转换、分子名称转SMILES

## 📋 系统要求

- Python 3.8+
- FastAPI
- Uvicorn
- 其他依赖包（见 requirements.txt）

## 🛠️ 安装和配置

### 1. 克隆项目
```bash
git clone <your-repository-url>
cd Chemistry_Agent
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 设置环境变量

#### 🪟 Windows 用户（推荐使用脚本）

**方法1: 使用批处理脚本**
```cmd
# 双击运行 setup_env_windows.bat
# 或右键 -> 以管理员身份运行
```

**方法2: 使用PowerShell脚本**
```powershell
# 右键 setup_env_windows.ps1 -> 以管理员身份运行PowerShell
# 或在PowerShell中运行：
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\setup_env_windows.ps1
```

**方法3: 手动设置**
1. 右键"此电脑" -> 属性 -> 高级系统设置 -> 环境变量
2. 在"用户变量"中点击"新建"
3. 变量名输入 `OPENAI_API_KEY`，变量值输入你的API密钥
4. 重复步骤2-3添加其他API密钥

**方法4: 命令行临时设置**
```cmd
# CMD
set OPENAI_API_KEY=your_openai_api_key
set SERP_API_KEY=your_serp_api_key
```

```powershell
# PowerShell
$env:OPENAI_API_KEY = "your_openai_api_key"
$env:SERP_API_KEY = "your_serp_api_key"
```

#### Windows PowerShell:
```powershell
# 必需的环境变量
$env:OPENAI_API_KEY = "your_openai_api_key"

# 可选的环境变量
$env:SERP_API_KEY = "your_serp_api_key"
$env:RXN4CHEM_API_KEY = "your_rxn4chem_api_key"
$env:CHEMSPACE_API_KEY = "your_chemspace_api_key"
$env:SEMANTIC_SCHOLAR_API_KEY = "your_semantic_scholar_api_key"
```

#### Windows CMD:
```cmd
# 必需的环境变量
set OPENAI_API_KEY=your_openai_api_key

# 可选的环境变量
set SERP_API_KEY=your_serp_api_key
set RXN4CHEM_API_KEY=your_rxn4chem_api_key
set CHEMSPACE_API_KEY=your_chemspace_api_key
set SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key
```

#### Linux/Mac:
```bash
# 必需的环境变量
export OPENAI_API_KEY="your_openai_api_key"

# 可选的环境变量
export SERP_API_KEY="your_serp_api_key"
export RXN4CHEM_API_KEY="your_rxn4chem_api_key"
export CHEMSPACE_API_KEY="your_chemspace_api_key"
export SEMANTIC_SCHOLAR_API_KEY="your_semantic_scholar_api_key"
```

#### 通过系统设置（推荐）:
1. 右键"此电脑" -> 属性 -> 高级系统设置 -> 环境变量
2. 在"用户变量"中点击"新建"
3. 变量名输入 `OPENAI_API_KEY`，变量值输入你的API密钥
4. 重复步骤2-3添加其他API密钥

## 🚀 快速开始

### 方法1: 使用启动脚本
```bash
python start_server.py
```

### 方法2: 直接启动
```bash
cd app
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 方法3: 使用uvicorn
```bash
cd app
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

## 📚 API 文档

启动服务器后，访问以下地址查看API文档：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔧 API 端点

### 基础端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API根路径，返回基本信息 |
| `/health` | GET | 健康检查 |
| `/api/info` | GET | 获取API详细信息 |

### ChemAgent 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/chemagent/` | POST | 与ChemAgent聊天 |
| `/api/chemagent/health` | GET | ChemAgent健康检查 |
| `/api/chemagent/tools` | GET | 获取可用工具列表 |

## 💬 使用示例

### 1. 基础聊天
```python
import requests

url = "http://localhost:8000/api/chemagent/"
payload = {
    "input": "计算苯的分子量",
    "model": "gpt-4-0613",
    "tools_model": "gpt-3.5-turbo-0613",
    "temperature": 0.1,
    "max_iterations": 10,
    "streaming": False,
    "local_rxn": False,
    "api_keys": {}
}

response = requests.post(url, json=payload)
result = response.json()
print(result['output'])
```

### 2. 合成规划
```python
payload = {
    "input": "如何合成阿司匹林？",
    "model": "gpt-4-0613",
    "temperature": 0.1,
    "max_iterations": 20
}

response = requests.post(url, json=payload)
result = response.json()
print(result['output'])
```

### 3. 安全性检查
```python
payload = {
    "input": "检查硝化甘油的安全性",
    "model": "gpt-4-0613",
    "temperature": 0.1
}

response = requests.post(url, json=payload)
result = response.json()
print(result['output'])
```

## 🧪 测试

运行测试脚本：
```bash
python test_chemagent.py
```

测试脚本会：
- 检查API健康状态
- 获取API信息
- 测试ChemAgent功能
- 进行示例对话

## 🔧 配置选项

### 模型配置
- `model`: 主要LLM模型 (默认: "gpt-4-0613")
- `tools_model`: 工具选择模型 (默认: "gpt-3.5-turbo-0613")
- `temperature`: 模型温度 (默认: 0.1)
- `max_iterations`: 最大迭代次数 (默认: 40)

### 功能配置
- `streaming`: 是否使用流式输出 (默认: False)
- `local_rxn`: 是否使用本地反应工具 (默认: False)
- `api_keys`: 自定义API密钥配置

## 🛡️ 错误处理

API包含完善的错误处理机制：

- **404错误**: 端点不存在
- **500错误**: 服务器内部错误
- **验证错误**: 请求参数验证失败
- **ChemAgent错误**: 智能体执行失败

## 📝 日志

服务器会记录详细的日志信息，包括：
- 请求处理时间
- 错误信息
- ChemAgent执行状态
- API调用统计

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📄 许可证

本项目采用 MIT 许可证。

## 📞 联系方式

如有问题，请联系：
- 作者: Jun YU
- 邮箱: [your-email@example.com]

---

**注意**: 请确保在使用前正确配置所有必需的API密钥，某些功能可能需要特定的API访问权限。

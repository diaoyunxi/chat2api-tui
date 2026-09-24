# Chat2API TUI Client

基于 [Chat2API](https://github.com/xiaoY233/Chat2API) 的命令行智能体客户端，支持多模态视觉分析、热加载工具系统和智能体循环。

## 📖 项目简介

Chat2API TUI Client 是一个轻量级的命令行工具，通过 Chat2API 服务将 DeepSeek、GLM、Kimi、Qwen 等主流 AI 模型的 Web 端能力转换为 OpenAI 兼容的 API 接口。本项目在此基础上提供了：

- **多模态支持**：上传图片供视觉模型分析
- **外置工具系统**：工具定义在独立 Python 文件中，通过文件头部注释声明，支持热加载无需重启
- **智能体循环**：自动检测模型输出的工具调用，执行后自动将结果带回对话，支持多轮工具调用
- **对话管理**：多轮上下文、持久化保存/加载、系统提示词设置
- **内置工具**：文件读写、系统命令执行、用户询问

## 🎯 依赖项目

### 核心依赖：Chat2API 服务端

本项目是 Chat2API 的客户端，**使用前必须先部署 Chat2API 服务端**。

Chat2API 服务端支持以下 AI 服务商：

| 服务商 | 认证类型 | 支持模型 |
|--------|----------|----------|
| DeepSeek | User Token | deepseek-v4-flash, deepseek-v4-pro |
| GLM (智谱清言) | Refresh Token | GLM-5.1 |
| Kimi | JWT Token | Kimi-K2.6 |
| MiniMax | JWT Token | MiniMax-M2.7 |
| Qwen (通义千问) | SSO Ticket / JWT Token | Qwen3.6, Qwen3.7-Max, Qwen3.5-Flash 等 |
| Perplexity | Cookie | Auto |

> **注意**：Chat2API 有多个分支版本。本项目基于 **xiaoY233/Chat2API**开发，推荐使用该版本。

### Python 依赖

- **Python 3.8+**
- **openai >= 1.0.0** — OpenAI 兼容客户端
- **pyyaml >= 6.0** — 配置文件解析

## 📦 安装

### 1. 克隆项目

```bash
git clone https://github.com/diaoyunxi/chat2api-tui.git
cd chat2api-tui
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置文件

复制示例配置文件并填写你的配置：

```bash
cp config.example.yml config.yml
```

编辑 `config.yml`：

```yaml
# Chat2API 服务地址（注意末尾带 /v1）
base_url: "http://127.0.0.1:8080/v1"

# 本地 API Key（在 Chat2API Web 管理界面生成）
api_key: "sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 默认使用的模型
default_model: "deepseek-v4-flash"

# 支持的模型列表
supported_models:
  - "deepseek-v4-flash"
  - "deepseek-v4-pro"
```

### 4. 启动 Chat2API 服务端

按照 [Chat2API 官方文档](https://chat2api-doc.vercel.app/)部署服务端，确保服务正常运行在 `http://127.0.0.1:8080`。

### 5. 运行客户端

```bash
python app.py
```

## 🚀 使用方法

启动后进入交互式命令行界面，**直接输入文本即为发送消息**，智能体会自动判断是否需要调用工具。

### 基本命令

| 命令 | 说明 |
|------|------|
| `/new` | 新对话（自动保存旧对话） |
| `/save` | 保存当前对话 |
| `/load [id]` | 列出所有对话 或 加载指定 ID |
| `/system [文本]` | 查看或设置系统提示词 |
| `/image [路径]` | 附加图片用于多模态分析 |
| `/reload` | 热加载 `tools/` 目录下的工具 |
| `/history` | 显示当前对话历史 |
| `/model [pro\|flash]` | 切换模型（默认 flash） |
| `/stream on/off` | 切换流式输出（实验性） |
| `/exit` | 退出（自动保存） |
| `/help` | 显示帮助 |

### 使用示例

```bash
# 启动客户端
$ python app.py

╔══════════════════════════════════════════════════════════╗
║  🤖 Chat2API 智能体客户端                              ║
║  输入消息直接对话  |  /help 查看命令                   ║
╚══════════════════════════════════════════════════════════╝

你> 你好，请介绍一下你自己
🤖 AI: 你好！我是 DeepSeek 开发的 AI 助手...

你> /image ~/photo.png
🖼️  已附加图片: photo.png

你> 这张图片里有什么？
🤖 AI: 这张图片显示的是...

你> /model deepseek-v4-pro
✅ 已切换到模型: deepseek-v4-pro

你> /reload
✅ 工具已重载
```

## 🔧 工具系统

### 内置工具

项目默认提供四个内置工具，位于 `tools/` 目录：

| 工具 | 功能 | 文件 |
|------|------|------|
| `read_file` | 读取指定路径的文件内容 | `tools/read_file.py` |
| `write_file` | 将内容写入指定路径的文件 | `tools/write_file.py` |
| `exec_cmd` | 执行系统命令并返回输出结果 | `tools/exec_cmd.py` |
| `ask_user` | 向用户询问问题并等待输入答案 | `tools/ask_user.py` |

### 自定义工具

在 `tools/` 目录下创建新的 `.py` 文件，**文件头部必须包含 `# tool:` 注释声明**：

```python
# tool: {"name": "calculate", "description": "执行数学计算"}
def calculate(expression: str) -> str:
    """执行数学计算"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {e}"
```

修改或新增工具后，在客户端输入 `/reload` 即可热加载，**无需重启程序**。

## 📁 项目结构

```
chat2api-tui-client/
├── app.py                  # 主程序入口
├── agent.py                # 智能体循环核心
├── requirements.txt        # Python 依赖
├── config.example.yml      # 配置文件示例
├── .gitignore              # Git 忽略文件
├── core/
│   ├── __init__.py
│   ├── config.py           # 配置加载
│   ├── llm_client.py       # OpenAI 兼容客户端
│   ├── tool_loader.py      # 工具热加载器
│   └── conversation.py     # 对话管理（持久化）
├── tools/                  # 外置工具目录
│   ├── read_file.py
│   ├── write_file.py
│   ├── exec_cmd.py
│   └── ask_user.py
└── data/
    └── conversations/      # 对话历史 JSON 文件
```

## ⚠️ 注意事项

1. **必须部署 Chat2API 服务端**：本项目是客户端，需要 Chat2API 服务端提供 API 服务。
2. **API Key 安全**：`config.yml` 包含敏感信息，已加入 `.gitignore`，请勿提交到版本控制系统。
3. **网络环境**：Chat2API 服务端需要能稳定访问目标 AI 平台的 Web 服务。
4. **仅供学习测试**：本项目通过非官方渠道调用模型，**请勿用于商业用途**，仅限个人学习与测试。
5. **工具执行风险**：`exec_cmd` 工具可执行系统命令，请谨慎使用，避免执行危险操作。

## 📄 许可证

本项目仅供学习参考，封号等后果概不负责，使用请遵守相关法律法规及平台规范。

## 🔗 相关链接

- [Chat2API 官方文档](https://chat2api-doc.vercel.app/)
- [Chat2API GitHub 仓库](https://github.com/xiaoY233/Chat2API)
- [Chat2API 支持的服务商文档](https://github.com/xiaoY233/Chat2API/blob/main/docs/providers/README.md)

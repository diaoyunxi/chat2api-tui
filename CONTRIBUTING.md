# 贡献指南

感谢你对 Chat2API TUI 的关注！

## 开发环境

```bash
git clone https://github.com/diaoyunxi/chat2api-tui.git
cd chat2api-tui
pip install -r requirements.txt
```

## 项目结构

- `agent.py` — 智能体循环主入口
- `core/` — 核心模块（配置、LLM 客户端、对话管理、工具加载）
- `tools/` — 内置工具（命令执行、文件读写、提问、停止）
- `widgets/` — TUI 界面组件

## 代码风格

- Python 代码遵循 PEP 8，使用 [ruff](https://github.com/astral-sh/ruff) 检查
- 运行 `ruff check .` 验证代码风格

## 提交 PR 流程

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交变更：`git commit -m "feat: add your feature"`
4. 推送分支并创建 Pull Request

## 提交信息规范

- `feat:` 新功能
- `fix:` 修复 Bug
- `docs:` 文档变更
- `refactor:` 代码重构
- `chore:` 构建/工具变更

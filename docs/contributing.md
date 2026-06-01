# 贡献指南

感谢你对 CV-Doctor 的关注！

## 开发环境

```bash
git clone https://github.com/your-username/cv-doctor.git
cd cv-doctor
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## 运行测试与 CI（与 GitHub Actions 一致）

```bash
# Server（P0 路径）
cd server && uv sync --extra dev --frozen && uv run pytest -q
cd server && uv run ruff check src/main.py src/api/schemas.py src/p0_models.py src/services/

# Web
cd web && npm ci && npm run build

# Worker（需 Node 22+）
cd worker && npm ci && npm run typecheck
```

## 代码规范

- P0 后端：Ruff 仅覆盖 `server/src/main.py`、`api/`、`p0_models.py`、`services/`（见 CI）
- 类型提示完整；API 契约以 `api/schemas.py` + `p0_models.py` 为准
- 长期域模型与 PolicyGuard：`server/src/models.py`
- 完整 LLM 管线：LiteLLM + 环境变量（P0 stub 阶段可不启用）

## 提交规范

- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 文档与 Agent 规范

**完整读档顺序、权威层级与实现态对照**见 [architecture.md §1.5](./architecture.md#15-文档与-agent-规范索引)。

| 文档 | 用途 |
|------|------|
| [architecture.md](./architecture.md) | 系统架构、Pipeline、文档地图 |
| [p0-mvp-implementation.md](./p0-mvp-implementation.md) | 当前迭代任务与 API |
| [../CLAUDE.md](../CLAUDE.md) | Claude Code / 完整 Agent 说明 |
| [../AGENTS.md](../AGENTS.md) | 跨工具 Agent 摘要 |
| [../skills/karpathy-guidelines/SKILL.md](../skills/karpathy-guidelines/SKILL.md) | 可安装到 `~/.cursor/skills` 的通用行为技能 |
| [../.cursor/rules/](../.cursor/rules/) | Cursor 项目规则（自动按 glob 生效） |

PR 前请阅读 [CLAUDE.md §5](../CLAUDE.md#5-pr-与-review-规则)（`@copilot review`、`@codex review`、CI 绿灯）。

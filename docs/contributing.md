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

## 运行测试

```bash
pytest
```

## 代码规范

- 使用 Ruff 进行代码检查
- 类型提示必须完整
- Pydantic 模型用于所有数据结构
- 所有 LLM 调用通过 LiteLLM 统一接口

## 提交规范

- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
- test: 测试
- chore: 构建/工具

## 文档与 Agent 规范

| 文档 | 用途 |
|------|------|
| [architecture.md](./architecture.md) | 系统架构（与 P0 方案一致） |
| [p0-mvp-implementation.md](./p0-mvp-implementation.md) | 当前迭代任务与 API |
| [../CLAUDE.md](../CLAUDE.md) | Claude Code / 完整 Agent 说明 |
| [../AGENTS.md](../AGENTS.md) | 跨工具 Agent 摘要 |
| [../skills/karpathy-guidelines/SKILL.md](../skills/karpathy-guidelines/SKILL.md) | 可安装到 `~/.cursor/skills` 的通用行为技能 |

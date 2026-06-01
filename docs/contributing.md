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

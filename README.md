# 🩺 CV-Doctor 简历对症下药

<p align="center">
  <strong>面向中文普通求职者的 AI 简历对症下药 Web 工具</strong>
</p>

<p align="center">
  上传简历 → 粘贴 JD → 获取可审计的优化建议 → 导出简历
</p>

---

## 为什么需要 CV-Doctor？

很多求职者把简历和 JD 丢给 ChatGPT 说"帮我优化"，但得到的结果：
- ❌ 不知道改了什么、为什么改
- ❌ 可能编造了你没有的经历
- ❌ 看不出和目标岗位的差距在哪

CV-Doctor 不同：
- ✅ **可审计修改** — 每条修改都有原文、改文、依据、风险
- ✅ **反幻觉** — 没有证据的经历不会写进简历
- ✅ **公司理解** — 基于官网/App/JD 理解目标公司，不只是关键词匹配
- ✅ **中文优先** — 适配 BOSS/拉勾/猎聘等中文 JD 语境

---

## 快速开始

### Web 版（推荐）

访问 [cv-doctor.com](https://cv-doctor.com)（即将上线）

### 本地运行

```bash
git clone https://github.com/your-username/cv-doctor.git
cd cv-doctor

# 后端
cd server
pip install -e .
cp .env.example .env  # 填入 DeepSeek API Key
uvicorn src.main:app --reload

# 前端
cd ../web
npm install
npm run dev
```

### CLI（开发者/本地隐私版）

```bash
pip install cv-doctor
cv-doctor diagnose resume.md --jd-file jd.txt
```

---

## 使用流程

```
1. 上传简历 (PDF/DOCX)
   ↓
2. 粘贴 JD 或输入目标公司+岗位
   ↓
3. 系统分析匹配度和差距
   ↓
4. 逐条审阅修改建议（接受/拒绝/编辑）
   ↓
5. 导出优化后简历 (DOCX/PDF)
```

---

## 核心功能

### 📊 Match Score 四维评分
- 必须项覆盖 (40%): JD must-have 是否有简历证据
- 关键词覆盖 (25%): 技能、工具、领域词覆盖
- 经历相关性 (25%): 项目经历是否支持岗位要求
- 表达与格式 (10%): 动词、量化、可读性

### 📋 可审计修改
每条修改都有：
- 原文 → 改后
- 修改依据（来自 JD 第 X 条 / 来自公司官网）
- 事实风险等级
- 用户可逐条接受/拒绝/编辑

### 🏢 公司理解（Target Mode）
- 官网/App/JD 多源分析
- 产品、业务、文化、技术栈提取
- 简历策略建议

### 🛡️ 反幻觉机制
- Evidence Store 事实账本
- Policy Guard 安全策略
- 没有证据的内容不进入简历

---

## 技术栈

| 模块 | 技术 |
|------|------|
| 前端 | Next.js + React + Tailwind |
| 后端 | FastAPI + Python |
| 默认模型 | DeepSeek V4 Flash |
| 深度模型 | Kimi K2.6 |
| 本地模型 | Ollama |
| LLM 路由 | LiteLLM |
| 数据模型 | Pydantic v2 |
| 数据库 | PostgreSQL |
| 队列 | Redis |

---

## 项目结构

```
cv-doctor/
├── web/           # 前端 (Next.js)
├── server/        # 后端 (FastAPI) + 核心引擎
├── cli/           # CLI 开源内核 (P3)
└── docs/          # 文档
```

---

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](docs/contributing.md)。

---

## 许可证

[MIT License](LICENSE)

---

## 致谢

- [DeepSeek](https://deepseek.com) — 默认 LLM 提供商
- [Kimi](https://kimi.moonshot.cn) — 深度分析模型
- [LiteLLM](https://github.com/BerriAI/litellm) — LLM 统一接口
- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) — PDF 解析

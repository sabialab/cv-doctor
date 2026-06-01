# CLAUDE.md — CV-Doctor

本文件是本仓库的**最高执行标准**。所有 AI coding agent（Claude Code、Codex、Copilot、Cursor 等）在本仓库工作时必须以本文件为准。`AGENTS.md` 是跨工具摘要；与本文件冲突时**以本文件为准**。

---

## 0. Superpowers 插件 — 会话级最高优先级

> Cursor 中已安装 **Superpowers** 插件时，**无论任务大小、无论是否仅回答问题**，都必须**优先**调用 Superpowers 技能，再执行其他动作。项目规则：`.cursor/rules/superpowers.mdc`（`alwaysApply: true`）。

### 0.1 何时必须调用

| 时机 | 要求 |
|------|------|
| **每次会话开始** | 先读 `using-superpowers`（如何发现与调用技能） |
| **任何创意/功能/行为改动前** | `brainstorming` |
| **按书面计划实施** | `executing-plans` 或 `subagent-driven-development` |
| **实现功能或修 bug** | `test-driven-development` |
| **遇到失败、异常行为** | `systematic-debugging` |
| **声称完成/通过/已修复前** | `verification-before-completion`（必须跑验证命令） |
| **收到 code review 反馈** | `receiving-code-review` |
| **大步骤完成、合并前** | `requesting-code-review` |
| **多步需求尚无计划** | `writing-plans` |

**禁止**因「任务很小」而跳过 Superpowers；选最轻量的对应技能即可。

### 0.2 与本文其他章节的关系

- **Superpowers** 规定 *工作方式*（技能、TDD、完成前验证）。
- **§1 Karpathy** 规定 *代码行为*（简单、精准改动）。
- **§2–3** 规定 CV-Doctor *产品与信任边界*。

若在**产品安全**（如反幻觉、PolicyGuard）上 Superpowers 技能与 §2–3 冲突，**以 §2–3 为准**。

### 0.3 非 Cursor 环境

Codex / Copilot 等无 Superpowers 插件时：按上表**同等流程**手动执行（先规划/验证清单，再动手），详见 [`AGENTS.md`](AGENTS.md) 与 [`CURSOR.md`](CURSOR.md)。

---

## 1. 通用行为准则（Andrej Karpathy 风格）— 代码层第一优先级

> 完整条文见 `.cursor/rules/karpathy-guidelines.mdc` 与 [`skills/karpathy-guidelines/SKILL.md`](skills/karpathy-guidelines/SKILL.md)。上游参考：[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)。

**Tradeoff:** 准则偏向谨慎与可验证，而非速度。琐碎修改可酌情简化，但仍须遵守领域红线（见第 3 节）。

### 1.1 Think Before Coding

**不要假设。不要隐藏歧义。把权衡摆到台面上。**

实现前：明确假设；不确定就问；多种理解并存时列出来，不要静默选一条；有更简单做法就说；说不清就停下并提问。

### 1.2 Simplicity First

**用最少代码解决问题。不做 speculative 抽象。**

- 不做需求外的功能、一层又一层的抽象、为不可能场景写的防御代码。
- 若 200 行能写成 50 行，就重写。

### 1.3 Surgical Changes

**只动必须动的；只清理自己造成的孤儿代码。**

- 不顺手「改进」相邻格式、注释或无关重构。
- 你引入的无用 import/变量要删；**不要**删历史遗留死代码，除非用户明确要求。
- 每一行改动都应能追溯到用户请求或 review 意见。

### 1.4 Goal-Driven Execution

**先定义可验证的成功标准，再循环直到证据齐全。**

多步任务先写简短计划，每步附带 verify 方式（测试、build、dry-run 等）。禁止用「应该可以」代替实际命令输出。

---

## 2. 项目上下文

### 产品定位

**CV-Doctor（简历对症下药）** — 面向中文求职场景的可审计简历修改，不是「一键润色」或 ATS 刷分工具。

- **是**：粘贴 JD → 诊断差距 → 逐条审阅修改建议（原文/改文/依据/风险）→ 用户接受后再导出。
- **不是**：从零生成简历、无依据编造经历、把 JD 缺口直接写进简历当事实。

**界面文案**：简体中文（`zh-CN`）。代码注释与 agent 文档：英文或中英均可。

### 文档优先级（大改前必读）

| 优先级 | 文档 | 用途 |
|--------|------|------|
| 1 | `PLAN.md` | 愿景、阶段 P0–P3、边界 |
| 2 | `docs/p0-mvp-implementation.md` | 产品范围、里程碑、验收（功能目标） |
| 3 | `docs/p0-cloudflare-stack.md` | **部署与运行时**（Cloudflare 全栈；替代旧「Vercel + VPS」示意） |
| 4 | `docs/mvp-feasibility.md` | 可行性、风险 |
| 5 | `server/src/models.py` | 领域模型与 `PolicyGuard`（长期 schema） |
| 6 | `server/src/p0_models.py` | **当前 P0 API / 桩流水线** 用的诊断结构 |

若 `p0-mvp-implementation.md` 与 `p0-cloudflare-stack.md` 在存储层描述不一致：**部署以 `p0-cloudflare-stack.md` 为准**；功能验收仍以 P0 实现文档为准。

### 仓库布局

```text
cv-doctor/
├── server/          # FastAPI（本地 :8787；生产目标为 Cloudflare Container 镜像）
├── web/             # Next.js App Router + TypeScript + Tailwind
├── worker/          # Cloudflare Worker（Hono），边缘 /api 代理
├── cli/             # Typer，P0 非主路径，调试/隐私本地用
├── docs/            # 架构、贡献、P0 / CF 部署说明
├── .github/workflows/ci.yml
├── PLAN.md
├── CLAUDE.md        # 本文件
├── AGENTS.md
└── CURSOR.md        # Cursor 规则说明
```

### 技术栈与运行时（当前分支实情）

| 层级 | 选型 | 说明 |
|------|------|------|
| API（开发） | FastAPI + Pydantic v2，`uvicorn` | 入口 `server/src/main.py` |
| API（边缘） | Worker + Hono | `worker/src/index.ts`，`PIPELINE_URL` 指向上游 Python |
| 前端 | Next.js App Router | `web/`，`NEXT_PUBLIC_API_BASE` + 可选 `NEXT_PUBLIC_API_PREFIX` |
| 会话（**当前实现**） | 进程内 `SessionStore` | 内存会话；重启丢失；**目标** 为 D1 + R2（见 CF 文档） |
| 诊断（**当前实现**） | `stub_pipeline`（默认）或 `pipeline`（`USE_REAL_PIPELINE=1`） | 桩用于 CI；真实管线需 API Key |
| 领域 schema | `models.py` + `p0_models.py` | `PolicyGuard` 等在 `models.py`；P0 响应用 `p0_models` |
| LLM（完整流水线） | LiteLLM → DeepSeek 等 | 需 `DEEPSEEK_API_KEY`；桩模式不依赖 |
| 依赖管理（server） | `uv` + `uv.lock` | CI：`uv sync --extra dev --frozen` |
| CI | GitHub Actions | `server` / `web` / `worker` 三 job 并行 |

**Cloudflare 目标架构（文档已写，代码逐步对齐）：** Pages（前端）、Worker（API）、R2（`uploads/` 前缀）、D1（会话元数据）、Container（跑 `server/` 镜像）、Cron（TTL 清理）。本地开发可只跑 Python + Next，不启 Worker。

### P0 范围护栏

**当前迭代应默认实现/维护的：**

- Web：上传简历文件 + 粘贴 JD → 创建 session → 后台诊断 → 结果页轮询直至 `ready` 或 `failed`
- API：`POST /sessions`、`GET /sessions/{id}`、`PATCH .../changes/{id}`、导出、删除、隐私说明
- 结果页信息顺序：JD 解读 → 匹配/部分匹配/缺口 → ≤3 条修改建议（含风险）→ 匹配分（次要）
- 会话状态字段：`pending` | `processing` | `ready` | `failed`（**不要**擅自改成 `done`，除非同步改 `web/lib/api.ts`、测试与文档）

**明确不在 P0 默认范围（除非用户明确要求扩 scope）：**

- BOSS/拉勾/猎聘抓取、天眼查、公司画像、多 JD 并行、付费墙、账号体系
- 真实 DOCX 解析与合并导出（`USE_REAL_PIPELINE=1` 时解析+导出 DOCX；默认桩诊断）
- Kimi 深度报告、CLI 作为主入口、SEO 落地页矩阵

---

## 3. 仓库内特别注意

- **反幻觉优先**：不得编造简历事实；`PolicyGuard` / 高风险修改规则见 `llm-trust-boundary.mdc` 与 `server/src/models.py`
- **缺口（missing）** 只能作补充建议展示，**不得**写入简历当已具备经历
- **高风险修改** 不得在用户未明确接受时出现在导出结果中
- **不要** 把 `legacy` 的 `server/src/` 大段代码当作 P0 必改范围；CI 中 Ruff **仅**检查 P0 路径（见 `ci.yml`）
- **不要** 在 Worker 使用 Node 20 跑 Wrangler 4.x（CI 已固定 **Node 22**）
- **不要** 假设已有 D1/R2 绑定就能本地 `wrangler dev` 而不配 `PIPELINE_URL`；未配置时以 Python 直连为准
- **不要** 把原始简历/JD 打进第三方分析或日志；密钥只走 `.env` / `wrangler secret`，禁止提交
- 隐私文案：与 `docs/p0-cloudflare-stack.md` 一致——保留期 + 手动删除；**不要** 写死「24 小时自动删除」除非 TTL 与 Cron 已实现并上线

---

## 4. 验证清单

常规代码变更（按触及目录执行）：

```bash
# server（在 server/ 目录）
uv sync --extra dev --frozen
uv run ruff check \
  src/api src/main.py src/p0_models.py src/config.py \
  src/pipeline.py src/parser_resume.py src/parser_jd.py \
  src/facts.py src/gap_analyzer.py src/change_generator.py src/llm \
  src/services/session_store.py src/services/stub_pipeline.py \
  src/services/policy_guard.py src/services/export_guard.py \
  src/services/exporter_docx.py tests/
uv run pytest -q

# web（在 web/ 目录）
npm ci
NEXT_PUBLIC_API_BASE=http://127.0.0.1:8787 npm run build

# worker（在 worker/ 目录，需 Node ≥ 22）
npm ci
npx tsc --noEmit
PIPELINE_URL=http://127.0.0.1:8787 ALLOWED_ORIGINS=http://localhost:3000 npx wrangler deploy --dry-run
```

仅文档/配置变更至少：

```bash
git diff --check
```

触及 LLM/导出/PolicyGuard 时，在说明中写明如何考虑幻觉与高风险路径。

未跑的检查必须在最终回复中**写明原因**。

---

## 5. PR 与 Review 规则

- 创建 PR 或向 PR 推送修复后，应 push 当前分支并查看 PR checks（本仓库 CI：`server` / `web` / `worker`）
- 处理 review 时优先看 **未解决** 的 thread，再决定可否采纳；外部 reviewer 不是唯一真相来源
- **不要** 主动 resolve GitHub review threads，除非用户明确要求

### 强制 Review 触发（新 PR 或 push 修复后）

在对应 PR 上请求自动 review（文档与配置变更同样适用）：

```text
@copilot review
@codex review
```

推荐：

```bash
gh pr comment <PR_NUMBER> --body $'@copilot review\n@codex review'
```

若因权限或无法定位 PR 而无法触发，须在回复中说明。

**例外：** 用户明确要求合并进 `main` 时，不强制在合并前再触发上述 review（除非模板/CI 另有要求）。

### 本地 CodeRabbit CLI（push / 开 PR 前建议）

```bash
cr review --base main --plain
cr review --type uncommitted --plain
```

- P1/P2 应修复后再 push；P3 及以下可记录不阻塞
- `cr` 不可用须在说明中写明

---

## 6. 工作方式

- 先读代码再下结论；用 `rg` 找现有 helper/测试，再新增抽象
- 改动可追溯到用户请求或 review；不要回滚用户未授权的工作区内容
- 合并到 `main` 时默认 **Squash merge**（保持主干线性），除非维护者另有规定
- 完成前用第 4 节命令验证，不用「应该过了」代替日志

### 与其他 agent 文件同步

修改行为准则或 P0 边界时，同步更新：

- `CLAUDE.md`（本文件）
- `AGENTS.md`
- `.cursor/rules/superpowers.mdc`（Superpowers 路由变更时）
- `.cursor/rules/karpathy-guidelines.mdc`
- `.cursor/rules/cv-doctor-core.mdc`
- `.cursor/rules/llm-trust-boundary.mdc`（涉及信任边界时）

---

**准则生效标志：** diff 更少无关改动、少过度设计、问题在实现前提出、每个任务有可执行的 verify 输出。

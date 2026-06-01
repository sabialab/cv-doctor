# CLAUDE.md — CV-Doctor

本文件是本仓库的**最高执行标准**。所有 AI coding agent（Claude Code、Codex、Copilot、Cursor 等）在本仓库工作时必须以本文件为准。`AGENTS.md` 是跨工具摘要；与本文件冲突时**以本文件为准**。

**准则优先级（总序）：** **§1 Karpathy 通用行为（第一优先级）** → §0 Superpowers 技能工作流 → §2–3 产品与信任边界 → §5–7 PR / Review / 合并发布。

---

## 0. Superpowers 插件 — 技能工作流（在 §1 Karpathy 之后）

> Cursor 中已安装 **Superpowers** 插件时，在遵守 **§1** 的前提下，**无论任务大小**，须按技能路由调用 Superpowers（先读 `using-superpowers`）。项目规则：`.cursor/rules/superpowers.mdc`（`alwaysApply: true`）。

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

- **§1 Karpathy** 规定 *通用行为*（第一优先级：思考、简单、精准改动、可验证完成）。
- **Superpowers** 规定 *技能化工作流*（TDD、调试、完成前验证、review 技能）。
- **§2–3** 规定 CV-Doctor *产品与信任边界*。
- **§5–7** 规定 *Git / PR / Review / 合并发布*。

若在**产品安全**（反幻觉、PolicyGuard）上与其他章节冲突，**以 §2–3 为准**。

### 0.3 非 Cursor 环境

Codex / Copilot 等无 Superpowers 插件时：按上表**同等流程**手动执行（先规划/验证清单，再动手），详见 [`AGENTS.md`](AGENTS.md) 与 [`CURSOR.md`](CURSOR.md)。

---

## 1. 通用行为准则（Andrej Karpathy 风格）— 第一优先级

> **所有任务（含文档、PR、review 修复）均须遵守本节。** 完整条文见 `.cursor/rules/karpathy-guidelines.mdc` 与 [`skills/karpathy-guidelines/SKILL.md`](skills/karpathy-guidelines/SKILL.md)。上游：[multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills)。

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

## 5. Git 分支与 MVP 阶段工作流（强制）

> **禁止**在「已合并进 `main` 的旧 feature 分支」上继续堆下一阶段工作。否则 PR diff 会重复整段历史、易与 `main` 冲突、review 失真。

| 规则 | 说明 |
|------|------|
| 基线 | 每个新阶段从 **`git fetch origin && git checkout -b feat/<阶段>-<简述> origin/main`** 开始 |
| 一 PR 一目标 | 例如：`main` 已含 P0（#1）→ Phase 1 单独分支/PR，只含本阶段增量 |
| 误在旧分支开发 | `git reset --hard origin/main` 后 **`git cherry-pick`** 仅保留本阶段提交（勿 replay 已在 main 的提交） |
| 合并后 | 旧分支视为只读；下一阶段**新建**分支名 |

阶段划分见 `docs/p0-mvp-implementation.md`。开工前确认：`git log origin/main..HEAD` 不应重复 main 已有的大块提交。

---

## 6. GitHub PR 工作流

- 修复 PR review 时，先读取 **thread-aware / unresolved** review context，再判断哪些意见 **actionable**
- 提交或向 PR 推送修复后，**必须等待关键 CI/checks**，在回复中写明通过或失败原因（勿用「应该绿了」）
- 每次合并 PR 到 `main`，**必须**使用 **Squash and merge**（压缩合并）。**禁止** Merge commit 或 Rebase and merge，保证 `main` 线性、一 PR 一 commit
- 每次合并到 `main` 后，**必须**同步更新（非可选）：
  - 根目录 [`README.md`](README.md)
  - [`CHANGELOG.md`](CHANGELOG.md)（`[Unreleased]` → 新版本条目）
  - [`web/package.json`](web/package.json) 与 [`web/package-lock.json`](web/package-lock.json) 的 `version`
  - [`worker/package.json`](worker/package.json) 与 [`worker/package-lock.json`](worker/package-lock.json) 的 `version`
  - [`server/pyproject.toml`](server/pyproject.toml) 的 `version`（与上列版本号一致）
- 合并完成后：本地 `git checkout main && git pull origin main`；`git status` 须干净（无未提交变更、无应 push 未 push 的 commit）

---

## 7. PR 与 Review 规则

- 创建 PR 或修复已有 PR 后：**push 当前分支**并检查 PR checks（CI：`server` / `web` / `worker`）
- 修复 review 时：**不要只看扁平 comment**；优先获取 **unresolved review threads**
- 先技术评估 review 意见，再修复；外部 reviewer **不是**绝对正确来源
- **不要**主动 resolve GitHub review threads，除非用户明确要求

### 7.1 强制 Review 触发

每次**新建 PR**，或每次向已有 PR **推送修复**后，必须在对应 PR 上请求：

```text
@copilot review
@codex review
```

推荐：

```bash
gh pr comment <PR_NUMBER> --body $'@copilot review\n@codex review'
```

对文档、配置、版本号、CHANGELOG、README 更新**同样适用**。无法触发时须在最终回复中**明确说明**原因。

**例外：** 任务为**提出或执行**将 PR **合并进 `main`** 时，不强制在合并前再触发上述 review；仅当用户、维护者或 PR 模板/CI 明确要求时才触发。

### 7.2 本地 CodeRabbit CLI（push / 开 PR 前必做）

在 push 或创建 PR **之前**必须本地跑 CodeRabbit，**P1/P2 清零**后才允许 push：

```bash
# 对比 main 的已 commit 改动
cr review --base main --plain

# 未 commit 的草稿
cr review --type uncommitted --plain
```

- `--plain` 便于 agent 解析
- P1/P2 必须修复后重跑至 **0**；P3 及以下可记录，不阻塞
- `cr` 不可用（未安装、超时、权限）须在最终说明中写明；可分目录：`cr review --agent --dir server`

---

## 8. 工作方式

- 先读代码再下结论。**不要**根据文件名猜测行为
- 先用 `rg` 搜索现有 helper、测试和脚本，再新增抽象
- 改动须可追溯到用户请求或 review 意见；避免顺手改样式、格式或无关重构
- **不要**回滚或覆盖用户未授权的改动
- 遇到 review 意见：先评估，再修复
- 完成前**必须用实际命令验证**（见 §4），禁止用「应该可以」代替结果

### 与其他 agent 文件同步

修改 **Karpathy 准则**、**PR/分支工作流**或 P0 边界时，同步更新：

- `CLAUDE.md`（本文件）
- `AGENTS.md`
- `docs/contributing.md`
- `.cursor/rules/karpathy-guidelines.mdc`
- `.cursor/rules/pr-workflow.mdc`
- `.cursor/rules/superpowers.mdc`
- `.cursor/rules/cv-doctor-core.mdc`
- `.cursor/rules/llm-trust-boundary.mdc`（信任边界时）

---

**准则生效标志：** diff 更少无关改动、少过度设计、问题在实现前提出、每个任务有可执行的 verify 输出。

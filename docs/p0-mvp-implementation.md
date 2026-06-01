# P0 MVP 实施方案

> 基于 [PLAN.md](../PLAN.md) v3.2 与 [mvp-feasibility.md](./mvp-feasibility.md)  
> 周期：**2–4 周**（单人全职约 3 周可完成核心闭环）  
> 最后更新：2026-06-01

---

## 1. 目标与验收标准

### 1.1 一句话目标

证明：**普通用户愿意上传简历并粘贴 JD**，且认为 **比直接问 Kimi/DeepSeek 更可信**（有依据、可审阅、不瞎编）。

### 1.2 MVP 验收闭环（必须全部打通）

```text
上传 DOCX（或粘贴简历文本降级）
  → 粘贴 JD 文本
  → ≤45 秒看到首屏结果（手机可用）
  → 按顺序理解：JD 解读 → 匹配/部分/缺失 → 3 条免费 diff（≥1 条带风险说明）
  → 逐条 接受 / 拒绝 / 编辑
  → 下载应用修改后的 DOCX
```

### 1.3 Go / No-Go（上线后 2 周内）

| 指标 | 及格线 | 说明 |
|------|--------|------|
| 首页 → 完成上传+粘贴 | ≥20% | 漏斗入口 |
| 诊断任务成功率 | ≥70% | 解析+LLM 失败率可控 |
| 用户完成 3 条 diff 浏览 | ≥60% | 核心价值被看到 |
| 至少接受或编辑 1 条 | ≥40% | 审阅有价值 |
| 「比直接问 AI 好」主观认同 | ≥50% | 定性访谈/问卷 |
| 高风险修改写入最终稿 | **0%** | 反幻觉底线 |
| 首屏结果时间 | ≤45s | 手机耐心 |

**不看的指标：** 注册用户数、功能数量、是否上了付费。

**核心验证问题：** 「这个工具有没有让我更敢投这个岗位？」

---

## 2. 范围边界

### 2.1 In Scope（P0 必做）

| 模块 | 内容 |
|------|------|
| 入口 | Web/H5 单页应用，手机优先 |
| 输入 | 上传 DOCX；PDF/图片为尽力解析 + 粘贴降级；JD **仅用户粘贴文本** |
| 解析 | `python-docx` 结构化抽取 + `raw_text` 兜底 |
| 智能 | DeepSeek V4 Flash（LiteLLM），JSON Schema 强校验 |
| 输出 | Gap 报告 + Match Score + **3 条免费 Change**（展示可给 5 条，免费额度 3 条） |
| 审阅 | Diff UI：原文 / 改文 / 依据 / 风险 / 接受·拒绝·编辑 |
| 导出 | 仅合并 **已接受** 的 Change 到 DOCX |
| 隐私 | 上传旁说明、24h 自动删、一键删、不训练承诺 |
| 存储 | 会话级临时文件（本地目录或 MinIO），元数据可选 SQLite |

### 2.2 Out of Scope（明确不做）

- CLI 作为主入口（保留 `cli/` 仅内部调试）
- BOSS/拉勾 URL 自动抓取、登录态采集
- 天眼查 / 公司官网 / App 画像（→ P1 Target Mode）
- 多 JD、岗位版本管理（→ P2）
- Kimi K2.6 深度报告、Ollama 本地版（→ P3）
- 付费墙完整商业化（P0 可预留「完整导出」按钮占位，默认全开免费验证）
- 用户账号体系（P0 建议 **免登录会话 ID**，降低摩擦）
- PDF 导出质量版、模板市场、订阅制

---

## 3. 用户旅程与页面

### 3.1 页面清单（最少 3 页）

| 路由 | 页面 | 职责 |
|------|------|------|
| `/` | 落地/诊断页 | 上传 + 粘贴 JD + 隐私勾选/说明 + 提交 |
| `/s/[id]` | 结果页 | 五段式结果 + diff 卡片 + 导出 |
| `/privacy` | 隐私说明 | 静态页，链接放上传区旁 |

### 3.2 结果页信息架构（顺序不可打乱）

1. **岗位在招什么人** — JD 大白话摘要（3–5 句）
2. **你已匹配** — `full` 列表，带简历证据摘录
3. **部分匹配** — `partial` + 缺什么
4. **缺失项** — `missing` + 「不能编造，只能写进待补充建议」
5. **简历手术建议（免费 3 条）** — Diff 卡片列表

Match Score 放在第 2 节后作为 **反馈条**，不作为首屏主视觉。

### 3.3 Diff 卡片字段（与 `Change` 模型对齐）

```text
建议修改 1 / 3
原文：……
建议：……
依据：简历「…」；JD「…」
风险：低 / 中 / 高（中高风险默认需确认才写入）
[接受] [拒绝] [编辑]
```

---

## 4. 技术架构（P0 精简版）

### 4.1 推荐栈

| 层 | 选型 | 备注 |
|----|------|------|
| 前端 | Next.js 15 + React 19 + Tailwind 4 | 已有 `web/package.json` 骨架 |
| 后端 | FastAPI + Python 3.11+ | 新增 `main.py` 与 services |
| LLM | LiteLLM → `deepseek/deepseek-chat` 或文档指定 V4 Flash 等价模型 | `.env` 配置 |
| 校验 | Pydantic v2 | **已有** `server/src/models.py` |
| DOCX 读 | python-docx | |
| DOCX 写 | python-docx | P0 必做 |
| 任务 | 同步 Pipeline（P0）→ 后台任务（P0.5 可选 Celery） | 先同步降低复杂度 |
| 存储 | 本地 `uploads/{session_id}/` | 生产换 MinIO + 定时清理 |

### 4.2 P0 不做异步队列的前提

- 单次诊断目标耗时 **≤45s**，Pipeline 串行执行可接受。
- 若 LLM 超时 >60s，前端显示分步进度（解析简历 → 分析 JD → 匹配 → 生成建议）。
- **P0.5** 再引入 Redis + 后台 worker（并发与重试）。

### 4.3 目录结构（目标态）

```text
cv-doctor/
├── web/                          # Next.js
│   ├── app/
│   │   ├── page.tsx              # 首页
│   │   ├── s/[id]/page.tsx       # 结果页
│   │   └── privacy/page.tsx
│   ├── components/
│   │   ├── UploadZone.tsx
│   │   ├── JdPaste.tsx
│   │   ├── GapSections.tsx
│   │   └── DiffCard.tsx
│   └── lib/api.ts
├── server/
│   └── src/
│       ├── main.py               # FastAPI 入口
│       ├── api/routes/sessions.py
│       ├── services/
│       │   ├── parser_resume.py
│       │   ├── parser_jd.py
│       │   ├── facts.py
│       │   ├── gap_analyzer.py
│       │   ├── change_generator.py
│       │   ├── policy_guard.py
│       │   └── exporter_docx.py
│       ├── llm/client.py
│       └── models.py             # 已有
└── docs/
    └── fixtures/                 # 样本简历+JD（测试用）
```

---

## 5. 后端 Pipeline 设计

### 5.1 步骤与产出

```text
SessionCreate(resume_file, jd_text)
  → Step1 parse_resume     → Resume + list[Fact]
  → Step2 parse_jd          → JobDescription
  → Step3 extract_facts     → EvidenceStore（合并 resume facts）
  → Step4 gap_analyze       → GapReport + MatchScore
  → Step5 generate_changes  → ChangeSet（5 条，前端仅免费展示 3 条）
  → Step6 policy_filter     → 剔除 forbidden；标记 needs_confirmation
  → 返回 DiagnosisResult DTO
```

**P0 跳过：** 公司研究（Step3 Target）、向量检索可选用简单关键词匹配代替 embedding。

### 5.2 API 契约（最小集）

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/v1/sessions` | `multipart`: resume(docx), jd_text；返回 `{ session_id }` |
| `GET` | `/api/v1/sessions/{id}` | 状态：`pending` / `processing` / `done` / `failed` + 结果 |
| `PATCH` | `/api/v1/sessions/{id}/changes` | 更新每条 change 状态：`accepted`/`rejected`/`edited` |
| `POST` | `/api/v1/sessions/{id}/export` | 返回 DOCX 文件流 |
| `DELETE` | `/api/v1/sessions/{id}` | 一键删除会话及文件 |
| `GET` | `/health` | 健康检查 |

### 5.3 核心 DTO：`DiagnosisResult`

```python
class DiagnosisResult(BaseModel):
    session_id: str
    jd_summary: str                    # 大白话
    match_score: MatchScore
    requirements: list[JobRequirement] # 带 match_level
    changes: list[Change]             # 全量 5 条
    free_change_limit: int = 3
    evidence_store: EvidenceStore    # 可选精简返回
```

### 5.4 LLM 调用次数（P0）

| 步骤 | 次数 | 温度 | 输出 |
|------|------|------|------|
| JD 结构化 | 1 | 0.1 | `JobDescription` JSON |
| 简历 Fact 抽取 | 1 | 0.1 | `list[Fact]` |
| Gap 解释 + JD 摘要 | 1 | 0.2 | 文本 + 结构化 gap |
| Change 生成 | 1 | 0.3 | `ChangeSet` |

合计约 **4 次** 调用/会话，成本约 ¥0.03–0.08/次（见可行性文档）。

### 5.5 Policy Guard（硬规则，必须代码实现）

```python
# 伪代码 — 写入前最后一道闸
for change in changes:
    action = policy.check_change(change)
    if action == FORBIDDEN:
        continue  # 不进入 UI
    if change.risk_level == HIGH:
        change.requires_user_confirmation = True
    if not change.evidence_ids:
        continue  # 无证据不进列表
```

**导出时：** 仅 `status == accepted` 且非 `forbidden` 的 change 写入 DOCX。

---

## 6. 实施阶段（建议 3 周）

### Phase 0：准备（第 0 周前半，2–3 天）

| # | 任务 | 产出 |
|---|------|------|
| 0.1 | 确认 DeepSeek API Key 与模型名 | `.env` 可跑通 |
| 0.2 | 收集 3 套 fixture：简历 DOCX + JD 文本 | `docs/fixtures/` |
| 0.3 | 定义 `DiagnosisResult` 与 API OpenAPI 草稿 | `server/src/api/schemas.py` |
| 0.4 | Next.js 初始化 `app/`、Tailwind、API 基址 | `web` 可 `npm run dev` |

### Phase 1：后端 Pipeline（第 0–1 周）

| # | 任务 | 产出 | 依赖 |
|---|------|------|------|
| 1.1 | `parser_resume.py` DOCX → Resume + raw_text | 单测 | 0.2 |
| 1.2 | `parser_jd.py` LLM → JobDescription | 单测 | 0.1 |
| 1.3 | `facts.py` 简历 Fact 抽取 | 单测 | 1.1 |
| 1.4 | `gap_analyzer.py` match_level + MatchScore | 单测 | 1.2, 1.3 |
| 1.5 | `change_generator.py` + `policy_guard.py` | 单测 | 1.4 |
| 1.6 | `exporter_docx.py` | 单测 | 1.1 |
| 1.7 | `main.py` + `routes/sessions.py` 串起全流程 | 集成测 | 1.1–1.6 |
| 1.8 | CLI `diagnose` 命令调用同一 Pipeline（可选） | 方便调试 | 1.7 |

**里程碑 M1：** `curl` 上传 fixture 能拿到完整 JSON 结果。

### Phase 2：前端闭环（第 1–2 周）

| # | 任务 | 产出 |
|---|------|------|
| 2.1 | 首页：上传 + JD 粘贴 + 隐私文案 | 可提交 |
| 2.2 | 提交后跳转 `/s/{id}`，轮询或 SSE 等待结果 | 等待态 |
| 2.3 | 结果页五段式布局 + Match Score 条 | 信息架构达标 |
| 2.4 | DiffCard 三态 + 本地 state 同步 PATCH | 审阅可用 |
| 2.5 | 导出按钮 → 下载 DOCX | 闭环完成 |
| 2.6 | 移动端响应式（375px 起） | 主路径可用 |

**里程碑 M2：** 浏览器完整走通闭环（无需登录）。

### Phase 3：隐私、稳定、上线（第 2–3 周）

| # | 任务 | 产出 |
|---|------|------|
| 3.1 | 上传前隐私弹层/文案（调用云模型、24h 删除、不训练） | 合规 |
| 3.2 | `DELETE /sessions/{id}` + 定时清理脚本 | 一键删 + 自动删 |
| 3.3 | 错误态：解析失败 → 引导粘贴简历全文 | 降级路径 |
| 3.4 | LLM 超时重试 1 次；失败友好提示 | 稳定性 |
| 3.5 | 基础限流（IP / session 每日 N 次） | 防刷 API |
| 3.6 | 部署：Cloudflare Pages + Worker + Container + R2/D1 | 公网可访问 |
| 3.7 | 找 5–10 个种子用户走一遍 + 记录反馈表 | 验证 |

**里程碑 M3：** 对外软上线，开始收集 Go/No-Go 指标。

### Phase 4（可选，不阻塞 M3）

- 简单 PDF 导出
- 付费墙 UI（¥9.9 完整版）仅埋点
- 2–3 个岗位案例静态页（SEO 冷启动，可手写 MDX）

---

## 7. 测试策略

### 7.1 单元测试

- `tests/test_models.py` — 已有，扩展边界用例
- `tests/test_parser_resume.py` — 金标准 fixture DOCX
- `tests/test_policy_guard.py` — forbidden / 无 evidence 必拒
- `tests/test_match_score.py` — 权重加权公式快照

### 7.2 集成测试

- 固定 JD + 固定简历 → 快照测试 LLM 输出结构（mock LLM）
- 一条 e2e：上传 → 结果 JSON schema 校验

### 7.3 人工验收清单（每次发版必做）

- [ ] 中文 JD（BOSS 风格）解析合理
- [ ] 没有出现「主导/负责」而无证据的改写
- [ ] 至少 1 条 change 带明确风险说明
- [ ] 导出 DOCX 可 WPS/Word 打开且修改已应用
- [ ] 删除会话后目录与 DB 记录均不存在

---

## 8. 部署方案（P0 最小）

**全 Cloudflare 栈**（见 [p0-cloudflare-stack.md](./p0-cloudflare-stack.md)）：

```text
[用户] → Cloudflare Pages (Next.js, web/)
         → Cloudflare Worker (Hono API, worker/)
              → R2：会话文件
              → D1：会话元数据
              → Cloudflare Container：Python 流水线 (server/)
              → Cron：24h 清理
              → 密钥：DEEPSEEK_API_KEY（仅 Container/Worker secret）
```

- 域名：Pages 主域；API 同域 `/api/*` 或 `api.` 子域
- CORS：仅允许 Pages 源
- 日志：请求 id + session_id，不记简历正文到日志（隐私）

---

## 9. 隐私与合规检查表（上线前签字）

| 项 | P0 要求 | 实现位置 |
|----|---------|----------|
| 上传前告知调用第三方云模型 | 必做 | 首页上传区下方 |
| 默认 24 小时删除原始文件 | 必做 | cron + `AUTO_DELETE_HOURS` |
| 用户一键删除 | 必做 | 结果页「删除本次数据」 |
| 不用于模型训练 | 必做 | 隐私页 + 首页短文案 |
| JD 仅用户粘贴 | 必做 | 不做爬虫 |
| 日志不落盘全文 | 建议 | 日志脱敏 |
| 免登录 | P0 建议 | UUID session，无手机号 |

---

## 10. 风险与对策（实施期）

| 风险 | 对策 | 负责人 |
|------|------|--------|
| DOCX 样式解析乱 | 导出基于段落文本替换，不强改样式；解析预览 | 工程 |
| LLM 编造 | evidence_ids 硬校验 + Policy + 导出过滤 | 工程 |
| 45s 超时 | 分步 loading；超时提示重试 | 前后端 |
| 用户不敢上传 | 免登录 + 隐私文案 + 删除按钮 | 产品文案 |
| 做成「又一个润色」 | 结果页顺序强制 JD 解读优先 | 产品 |

---

## 11. 与现有仓库差距（开工清单）

| 已有 | 待建 |
|------|------|
| `server/src/models.py` 完整领域模型 | `main.py`, `services/*`, `api/routes/*` |
| `server/src/cli.py` 占位命令 | CLI 调用 `services.pipeline` |
| `server/tests/test_models.py` | parser / policy / e2e 测试 |
| `web/package.json` | `app/` 页面与组件 |
| `PLAN.md` 产品定义 | 本文件 + 可选看板 Issue |

---

## 12. 建议的 Issue 拆分（可直接建 GitHub Issues）

1. `[P0] FastAPI 会话 API 骨架 + 文件上传`
2. `[P0] DOCX 解析与简历 Fact 抽取`
3. `[P0] JD 结构化 + Gap/MatchScore`
4. `[P0] Change 生成 + Policy Guard`
5. `[P0] DOCX 导出（仅 accepted changes）`
6. `[P0] Next.js 首页 + 结果页 + Diff UI`
7. `[P0] 隐私删除与 24h 清理`
8. `[P0] 部署与种子用户验证`

---

## 13. 总结

P0 不是「做完全部 PLAN」，而是 **只交付一个可演示、可度量、可传播的闭环**：

> 粘贴 JD → 看懂岗位与缺口 → 审阅 3 条有依据的修改 → 导出 DOCX  

技术上 **复用已有 `models.py`**，优先打通 `server` Pipeline 与 `web` 三页；CLI 与 Target Mode 一律后置。  

上线后只用 **接受率、主观信任、是否更敢投** 决定下一阶段，而不是堆功能。

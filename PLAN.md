# CV-Doctor 简历对症下药 — 项目方案 v3

> 面向中文普通求职者的 AI 简历对症下药 Web 工具。
> 不会编造经历，基于原始简历、目标 JD、公司官网/App 与公开招聘信息，
> 生成可审计的修改建议、差距报告和针对性简历版本。

## 项目定位（v3）

**一句话定位：** 面向中文普通求职者的 AI 简历对症下药 Web 工具。

**核心卖点：**
- 🌐 普通用户友好：Web/H5 上传简历，无需命令行、GitHub、API Key
- 🇨🇳 中文精投：适配 BOSS/拉勾/猎聘/校招官网等中文 JD 语境
- 🏢 公司理解：官网/App/JD 优先，天眼查仅做工商核验
- 📋 可审计修改：每条修改都有原文、改文、依据、风险
- 🛡️ 反幻觉：不编造经历，缺失项只做补充建议
- 🔒 隐私透明：云端临时处理，可一键删除；高级模式支持本地/自带 Key

**不是什么：**
- 不是简历生成器（不从零建简历）
- 不是 ATS 评分器（没有统一真实 ATS 标准）
- 不是求职自动化平台（不自动投递、不打招呼）
- 不是 CLI 工具（CLI 是开源内核，不是用户入口）
- 不是"帮你骗过系统"的工具

---

## 一、v2→v3 核心修正

### 1.1 产品入口：CLI → Web/H5

| | v2 | v3 |
|---|---|---|
| MVP 入口 | `cv-doctor diagnose resume.md` | 打开网页，上传简历，粘贴 JD |
| 目标用户 | 开发者、技术求职者 | 普通中文求职者（手机/电脑） |
| CLI 角色 | MVP 核心 | 开源内核 / 开发者版 / 本地隐私版 |
| 传播渠道 | GitHub | 小红书、即刻、公众号、BOSS 用户社群 |

**理由：** CNNIC 第 57 次报告显示中国手机网民 11.21 亿，手机上网比例 99.6%。
BOSS 直聘月活 6090 万。求职场景高度 App 化。
会用 CLI 的用户本来就更可能自己用 Kimi/DeepSeek/Claude 改简历。

### 1.2 数据源：天眼查 → 官网/App/JD

| | v2 | v3 |
|---|---|---|
| 公司画像主源 | 天眼查 API + 官网爬取 | 公司官网/App + BOSS JD |
| 天眼查角色 | 核心数据源 | 仅做工商主体核验和风险提示 |
| 数据源分层 | 未明确 | S0-S6 七级可信度分层 |

### 1.3 LLM 策略：统一 LiteLLM → 分工路由

| | v2 | v3 |
|---|---|---|
| 默认模型 | 用户自选（OpenAI/Ollama） | DeepSeek V4 Flash（成本低、速度快） |
| 深度模型 | 无 | Kimi K2.6（256K 上下文、多模态、推理强） |
| 本地模型 | 默认推荐 | 高级模式，不作为普通用户默认入口 |
| 路由策略 | 无 | 按任务类型自动路由 |

---

## 二、公司数据源策略（v3 新增）

### 2.1 Source Confidence Matrix

| 等级 | 来源 | 可用于简历改写 | 用途 |
|------|------|----------------|------|
| S0 | 用户简历原文、用户确认补充 | ✅ 可以 | 简历事实 |
| S1 | 用户粘贴的 JD、招聘官网 JD、BOSS JD | ✅ 标记为 JD 依据 | 岗位要求、关键词 |
| S2 | 公司官网、产品官网、官方 App 页面 | ✅ 不能编入用户经历 | 公司业务、产品、文化 |
| S3 | 官方技术博客、GitHub 组织、开源仓库 | ✅ 技术岗可用 | 技术栈、工程方向 |
| S4 | 天眼查/国家企业信用/企查查 | ❌ 不直接用于简历 | 工商核验、风险提示 |
| S5 | 新闻、公众号、媒体 | ⚠️ 谨慎使用 | 背景补充 |
| S6 | 员工评价、脉脉、小红书、知乎 | ❌ 不建议进入简历 | 面试准备、风险提示 |

**核心原则：** 公司资料可以影响"简历排序和表达重点"，但不能创造"候选人经历"。

### 2.2 CompanyProfile 拆分（v3）

```python
class CompanyIdentity(BaseModel):
    """工商主体 — 天眼查负责"""
    legal_name: str
    aliases: list[str]
    registration_status: str
    risk_flags: list[str]
    source: Literal["tianyancha", "qichacha", "gsxt", "manual"]

class CompanyWorkProfile(BaseModel):
    """业务画像 — 官网/App/JD 负责"""
    brand_name: str
    products: list[str]
    target_users: list[str]
    business_model: str
    culture_keywords: list[str]
    tech_stack: list[str]
    hiring_keywords: list[str]
    evidence: list[CompanyClaim]
```

**天眼查 = 这家公司是不是这个主体、有没有风险**
**官网/App/JD = 这家公司在做什么、招什么人、怎么展示自己**

### 2.3 BOSS 直聘的正确角色

BOSS 不是"公司画像权威源"，是中国求职语境中最强的**招聘意图源**。

| 方式 | 阶段 | 说明 |
|------|------|------|
| 用户手动复制 JD 文本 | P0 必做 | 合规、稳定 |
| 用户上传截图 / 分享文本 | P0/P1 | 适合移动端 |
| 用户粘贴 BOSS 职位链接后本地解析 | P1 谨慎 | 只做用户主动页面 |
| 自动登录批量抓取 | 不做 | 风险高 |
| 反检测爬虫 | 不做 | 和产品信任冲突 |

**BOSS 是用户授权输入源，不是平台自动采集源。**

### 2.4 官网/App 采集方式

| 输入方式 | 阶段 | 说明 |
|----------|------|------|
| 用户粘贴公司官网 URL | P0 必做 | 最稳、合规 |
| 用户粘贴 App Store / 应用市场链接 | P1 建议做 | 可拿产品介绍、版本更新 |
| 用户上传 App 截图 / 官网截图 | P1 建议做 | Kimi K2.6 多模态理解 |
| 自动搜索公司官网 | P2 | 需用户确认，防误匹配 |

**Target Mode 设计原则：**
输入公司名 → 系统给出候选官网/App/JD → 用户确认 → 系统分析
（降低"字节跳动"vs"抖音"vs"飞书"的误识别）

---

## 三、LLM 策略（v3 新增）

### 3.1 模型路由

```yaml
llm:
  default_fast:
    provider: deepseek
    model: deepseek-v4-flash
    use_cases:
      - resume_parse
      - jd_analyze
      - gap_report
      - rewrite_diff
      - quick_mode

  deep_research:
    provider: kimi
    model: kimi-k2.6
    use_cases:
      - target_mode_company_profile
      - multi_source_reasoning
      - app_screenshot_analysis
      - interview_highlights
      - long_context_report

  premium:
    provider: deepseek
    model: deepseek-v4-pro
    use_cases:
      - high_value_paid_report
      - complex_resume_strategy

  local_privacy:
    provider: ollama
    model: configurable
    use_cases:
      - user_local_mode
      - developer_mode
```

### 3.2 成本分析

| 任务 | 模型 | 原因 |
|------|------|------|
| 简历解析、JD 结构化、关键词抽取 | DeepSeek V4 Flash | 成本低（$0.14/1M input）、上下文长、JSON 输出 |
| 快速改写、措辞润色、diff 生成 | DeepSeek V4 Flash | 高频调用，成本敏感 |
| 公司资料综合、Target Report | Kimi K2.6 | 256K 上下文、推理能力、多模态 |
| App 截图/页面理解 | Kimi K2.6 | 支持图像输入 |
| 兜底模型 | DeepSeek V4 Pro | 复杂报告、高价值付费任务 |
| 本地隐私版 | Ollama | 高级用户，效果不承诺最强 |

### 3.3 产品包装

| 模式 | 模型 | 用户感知 |
|------|------|----------|
| 快速诊断 | DeepSeek V4 Flash | 1-2 分钟出报告，低价/免费额度 |
| 深度对症下药 | DeepSeek + Kimi K2.6 | 5-8 分钟，多源报告 |
| 本地隐私版 | Ollama | 高级用户，本地运行 |

---

## 四、隐私与合规（v3 修订）

### 4.1 隐私设计

| 能力 | 阶段 | 说明 |
|------|------|------|
| 上传前明确告知会调用云模型 | P0 必做 | 合规和信任基础 |
| 默认 24 小时自动删除原始简历 | P0 必做 | 降低风险 |
| 用户一键删除本次数据 | P0 必做 | 增强信任 |
| 不训练模型承诺 | P0 必做 | 写进隐私说明 |
| 手机号登录可选，不强制 | P1 建议 | 降低转化阻力 |
| BYO API Key | P2 | 技术用户增强项 |
| 本地桌面版 | P3 | 隐私卖点 |

### 4.2 合规要点

- 《个人信息保护法》：合法、正当、必要、诚信原则
- 《企业信息公示暂行条例》：天眼查类数据仅限工商维度
- BOSS 用户协议：禁止自动化采集，仅做用户授权输入
- App 个人信息收集：不超范围收集，用户可删除

---

## 五、核心功能设计（v3 修订）

### 5.1 产品路径

```
P0: Quick Mode（JD 对症下药）
  上传简历 → 粘贴 JD → 匹配分析 → 修改建议 → 导出

P1: 轻量 Target Mode（公司理解）
  输入公司官网/App → 提取公司画像 → 简历策略调整

P2: 精投模式（多 JD）
  同公司 3-5 条 JD → 共性要求 → 精投版本

P3: 开源 CLI / 本地版
  CLI + Ollama + Docker + 插件
```

### 5.2 三件套输出

| 产物 | 说明 | 用户价值 |
|------|------|----------|
| `optimized_resume.docx/pdf` | 优化后简历 | 可直接投递或继续编辑 |
| `surgery_report` | 手术报告 | 解释为什么这样改 |
| `changes.diff` | 修改 diff 审阅 UI | 逐条接受/拒绝/编辑 |

### 5.3 Match Score 四维评分

| 评分项 | 权重 | 说明 |
|--------|------|------|
| 必须项覆盖 | 40% | JD must-have 是否有简历证据 |
| 关键词覆盖 | 25% | 技能、工具、领域词覆盖 |
| 经历相关性 | 25% | 项目/工作经历是否支持岗位要求 |
| 表达与格式 | 10% | 动词、量化、可读性 |

---

## 六、技术架构（v3）

### 6.1 总体架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Next.js / React)                │
│  文件上传 | 简历编辑器 | diff 审阅 UI | 导出 | 用量      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    后端 (FastAPI / Python)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ Resume   │  │ JD       │  │ Company  │              │
│  │ Parser   │  │ Analyzer │  │ Research │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │              │              │                    │
│  ┌────▼──────────────▼──────────────▼─────┐             │
│  │           Evidence Store               │             │
│  │  Facts | Requirements | Claims         │             │
│  └────────────────┬───────────────────────┘             │
│                   │                                      │
│  ┌────────────────▼───────────────────────┐             │
│  │           Policy Guard                 │             │
│  │  Allowed | NeedsConfirm | Forbidden    │             │
│  └────────────────┬───────────────────────┘             │
│                   │                                      │
│  ┌────────────────▼───────────────────────┐             │
│  │           LLM Router                   │             │
│  │  DeepSeek V4 Flash | Kimi K2.6 | Ollama│             │
│  └────────────────┬───────────────────────┘             │
│                   │                                      │
│  ┌────────────────▼───────────────────────┐             │
│  │           Output Engine                │             │
│  │  DOCX | PDF | Surgery Report | Diff    │             │
│  └────────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    存储层                                │
│  PostgreSQL(元数据) | ObjectStorage(临时文件) | Redis(队列)│
└─────────────────────────────────────────────────────────┘
```

### 6.2 技术栈选型

| 模块 | 技术方案 | 理由 |
|------|----------|------|
| 前端 | Next.js + React + Tailwind | SSR、组件生态、老大的强项 |
| 后端 | FastAPI + Python 3.11+ | 异步、类型提示、LLM 生态 |
| PDF 解析 | PyMuPDF / pdfplumber | 宽松许可，稳定 |
| DOCX 解析 | python-docx | 成熟稳定 |
| 高级 PDF/OCR | marker-pdf [optional] | GPL-3.0，可选增强 |
| LLM 接口 | LiteLLM | 统一接口，已支持 DeepSeek/Moonshot |
| 默认模型 | DeepSeek V4 Flash | 成本低、速度快、JSON 输出 |
| 深度模型 | Kimi K2.6 | 256K 上下文、多模态、推理强 |
| 本地模型 | Ollama | 高级/隐私模式 |
| 结构化输出 | Pydantic v2 | JSON Schema 强校验 |
| DOCX 生成 | python-docx | P0 必做 |
| PDF 生成 | WeasyPrint | P1 引入 |
| 数据库 | PostgreSQL | 用户、任务、报告元数据 |
| 对象存储 | S3 / MinIO | 临时文件，默认 24h 删除 |
| 队列 | Redis + Celery/FastStream | 异步 LLM 任务 |
| 向量相似度 | scikit-learn | TF-IDF + 余弦相似度 |
| 测试 | pytest + fixtures | 样本简历 + JD |

### 6.3 核心 Pipeline

```
Step 1: 用户上传简历
  PDF/DOCX/图片/文本
  → 解析成结构化 Resume
  → 抽取简历 Fact → Evidence Store

Step 2: 用户输入 JD
  粘贴文本 / 上传截图 / 上传文件 / 粘贴 BOSS 分享文本
  → DeepSeek V4 Flash 结构化
  → JobRequirement (must-have / nice-to-have)
  → Evidence Store

Step 3: (Target Mode) 公司研究
  用户输入官网 URL / App 链接 / 截图
  → Kimi K2.6 多源分析
  → CompanyWorkProfile
  → Evidence Store

Step 4: Gap Analyzer
  每条 JD 要求寻找简历证据
  → full / partial / missing

Step 5: Policy Guard
  低风险：措辞优化、排序调整 → 直接应用
  中风险：能力强度提升、量化表达 → 待确认
  高风险：新增经历、技能、职责 → 待确认

Step 6: ChangeSet
  DeepSeek V4 Flash 生成修改集
  每条修改：原文 / 改文 / 依据 / 风险 / evidence_ids
  → 送入前端 diff 审阅 UI

Step 7: 用户审阅
  逐条接受 / 拒绝 / 手动编辑
  → 生成最终简历

Step 8: Export
  DOCX / PDF 导出
  Surgery Report 生成
```

---

## 七、数据模型（v3 修订）

```python
from pydantic import BaseModel
from typing import Literal

# ==================== 证据系统 ====================

class Fact(BaseModel):
    id: str
    text: str
    source: Literal["resume", "user_input", "jd", "company_source"]
    source_url: str = ""
    confidence: float = 1.0
    can_use_in_resume: bool = True
    requires_user_confirmation: bool = False

class EvidenceStore(BaseModel):
    facts: list[Fact] = []

# ==================== 安全策略 ====================

class Change(BaseModel):
    section: str
    original: str
    revised: str
    reason: str
    evidence_ids: list[str] = []
    risk_level: Literal["low", "medium", "high"] = "low"
    requires_user_confirmation: bool = False
    source_label: str = ""

class ChangeSet(BaseModel):
    changes: list[Change] = []

# ==================== Match Score ====================

class MatchScore(BaseModel):
    overall: float = 0.0            # 0-100
    mandatory_coverage: float = 0.0 # 40%
    keyword_coverage: float = 0.0   # 25%
    experience_relevance: float = 0.0 # 25%
    expression_quality: float = 0.0 # 10%

# ==================== 公司画像（v3 拆分）====================

class CompanyIdentity(BaseModel):
    """工商主体 — 天眼查负责"""
    legal_name: str
    aliases: list[str] = []
    registration_status: str = ""
    risk_flags: list[str] = []
    source: Literal["tianyancha", "qichacha", "gsxt", "manual"] = "manual"

class CompanyClaim(BaseModel):
    claim: str
    source_type: str
    source_url: str = ""
    collected_at: str = ""
    confidence: float = 0.5

class CompanyWorkProfile(BaseModel):
    """业务画像 — 官网/App/JD 负责"""
    brand_name: str
    products: list[str] = []
    target_users: list[str] = []
    business_model: str = ""
    culture_keywords: list[str] = []
    tech_stack: list[str] = []
    hiring_keywords: list[str] = []
    evidence: list[CompanyClaim] = []

# ==================== 简历 / JD / 报告 ====================

class Resume(BaseModel):
    name: str
    contact: dict = {}
    summary: str = ""
    experiences: list[dict] = []
    education: list[dict] = []
    skills: list[str] = []
    projects: list[dict] = []
    certifications: list[str] = []
    raw_text: str = ""

class JobRequirement(BaseModel):
    text: str
    category: str
    is_mandatory: bool = True
    weight: float = 0.5
    match_level: Literal["full", "partial", "missing"] = "missing"
    resume_evidence: str = ""

class JobDescription(BaseModel):
    title: str
    company: str
    location: str = ""
    description: str = ""
    requirements: list[JobRequirement] = []
    keywords: list[str] = []

class GapReport(BaseModel):
    match_score: MatchScore = MatchScore()
    requirements_analysis: list[JobRequirement] = []
    strengths: list[str] = []
    gaps: list[str] = []
    suggestions: list[str] = []

class SurgeryReport(BaseModel):
    match_score_before: MatchScore = MatchScore()
    match_score_after: MatchScore = MatchScore()
    gap_report: GapReport = GapReport()
    company_profile: CompanyWorkProfile | None = None
    interview_highlights: list[str] = []
    changes_summary: str = ""

    @property
    def score_improvement(self) -> float:
        return self.match_score_after.overall - self.match_score_before.overall

class OptimizationResult(BaseModel):
    original_resume: Resume
    optimized_resume: Resume
    changeset: ChangeSet
    surgery_report: SurgeryReport
    evidence_store: EvidenceStore = EvidenceStore()
```

---

## 八、项目结构（v3）

```
cv-doctor/
├── PLAN.md
├── README.md
├── LICENSE                     # MIT
│
├── web/                        # 前端 ← v3 新增
│   ├── package.json
│   ├── next.config.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx            # 首页：上传简历 + 粘贴 JD
│   │   │   ├── analyze/page.tsx    # 分析页：Match Score + 差距
│   │   │   ├── review/page.tsx     # 审阅页：diff 接受/拒绝
│   │   │   └── export/page.tsx     # 导出页：DOCX/PDF 下载
│   │   ├── components/
│   │   │   ├── FileUpload.tsx      # 文件上传组件
│   │   │   ├── DiffViewer.tsx      # 修改 diff 审阅组件（核心）
│   │   │   ├── MatchScoreCard.tsx  # Match Score 展示
│   │   │   └── ChangeCard.tsx      # 单条修改卡片
│   │   └── lib/
│   │       └── api.ts              # 后端 API 调用
│   └── public/
│
├── server/                     # 后端 ← v3 重组
│   ├── pyproject.toml
│   ├── src/
│   │   ├── main.py             # FastAPI 入口
│   │   ├── config.py           # 配置管理
│   │   ├── models.py           # Pydantic 数据模型
│   │   │
│   │   ├── parser/             # 简历解析
│   │   │   ├── pdf_parser.py   # PyMuPDF
│   │   │   ├── docx_parser.py  # python-docx
│   │   │   └── normalizer.py   # 统一输出
│   │   │
│   │   ├── evidence/           # 证据系统
│   │   │   ├── store.py
│   │   │   ├── fact_extractor.py
│   │   │   └── policy.py       # Policy Guard
│   │   │
│   │   ├── analyzer/           # 分析引擎
│   │   │   ├── jd_analyzer.py
│   │   │   ├── gap_analyzer.py
│   │   │   ├── match_scorer.py
│   │   │   └── company_analyzer.py
│   │   │
│   │   ├── optimizer/          # 优化引擎
│   │   │   └── resume_optimizer.py
│   │   │
│   │   ├── output/             # 输出模块
│   │   │   ├── docx_generator.py
│   │   │   ├── pdf_generator.py
│   │   │   ├── surgery_report.py
│   │   │   └── changes_diff.py
│   │   │
│   │   ├── collectors/         # 数据采集
│   │   │   ├── website_collector.py
│   │   │   └── app_collector.py
│   │   │
│   │   ├── llm/                # LLM 路由
│   │   │   ├── router.py       # 任务→模型路由
│   │   │   ├── deepseek.py     # DeepSeek V4 Flash/Pro
│   │   │   ├── kimi.py         # Kimi K2.6
│   │   │   ├── prompts.py
│   │   │   └── structured.py   # 结构化输出
│   │   │
│   │   └── api/                # API 路由
│   │       ├── upload.py
│   │       ├── analyze.py
│   │       ├── review.py
│   │       └── export.py
│   │
│   ├── tests/
│   │   ├── fixtures/
│   │   ├── test_parser.py
│   │   ├── test_evidence.py
│   │   ├── test_analyzer.py
│   │   └── test_policy.py
│   │
│   └── prompts/
│       ├── extract_resume.md
│       ├── analyze_jd.md
│       ├── compare_gap.md
│       ├── rewrite_evidence.md
│       └── company_research.md
│
├── cli/                        # CLI（P3 开源内核）
│   ├── pyproject.toml
│   └── src/
│       ├── cli.py
│       └── ...（复用 server 核心模块）
│
└── docs/
    ├── architecture.md
    ├── evidence_system.md
    ├── privacy.md
    └── contributing.md
```

---

## 九、实施路线（v3）

### P0: Web Quick MVP — 2-4 周
> 目标：证明普通用户愿意上传简历，并认为"这比直接问 Kimi/DeepSeek 更好用"

| 模块 | 内容 |
|------|------|
| Web/H5 首页 | 上传简历、粘贴 JD |
| 文件解析 | DOCX/PDF/Text（Markdown 不作为主入口） |
| JD 分析 | must-have / nice-to-have / keywords |
| 简历证据抽取 | Fact Ledger |
| 差距报告 | Match Score + 缺口解释 |
| 修改建议 | 5-10 条 evidence-based changes |
| 审阅 UI | 接受/拒绝/编辑 |
| 导出 | DOCX 优先，PDF 次之 |
| 模型 | DeepSeek V4 Flash |
| 隐私 | 24h 自动删除、一键删除、不训练说明 |

**暂不做：** CLI 主入口、天眼查、BOSS 自动采集、复杂公司画像、多 JD、本地模型、模板市场

### P1: 轻量 Target Mode — 4-6 周
> 目标：让"对症下药"开始和普通 AI 简历工具拉开差距

| 模块 | 内容 |
|------|------|
| 官网 URL 分析 | 用户输入官网，提取产品/业务/价值观 |
| App 链接/截图分析 | App Store 链接或用户上传截图 |
| BOSS/JD 分享文本导入 | 用户主动粘贴 |
| 公司证据链 | CompanyClaim 每条带来源 |
| Kimi K2.6 深度报告 | 多源综合分析 |
| 简历策略 | 项目排序、关键词表达、面试亮点 |
| 版本管理 | 同一简历生成多个岗位版本 |

### P2: 多 JD 精投 — 6-8 周
> 目标：把 CV-Doctor 做成"精投工具"

| 模块 | 内容 |
|------|------|
| 多 JD 输入 | 用户粘贴 3-5 条同公司 JD |
| 共性要求抽取 | 高频硬技能/软技能/业务关键词 |
| 岗位族画像 | 同公司同方向招聘偏好 |
| 简历版本对比 | A 公司版 vs B 公司版 |
| 高级导出 | DOCX/PDF 模板 |
| 付费功能 | 深度报告、版本管理、多次优化 |

### P3: 开源 CLI / 本地版 — 8-12 周
> 目标：把 CLI 作为开源内核推出

| 模块 | 内容 |
|------|------|
| CLI | 调试、批处理、本地模式 |
| Ollama 支持 | 隐私优先本地版 |
| BYO API Key | 技术用户自带 Key |
| Docker | 私有部署 |
| 插件机制 | 招聘平台导入、企业数据源 |
| GitHub 开源 | Engine 开源，Web 可部分闭源 |

---

## 十、关键设计决策（v3）

### 10.1 Diff 审阅 UI 是护城河

```markdown
建议修改 1 / 8

原文：
参与用户增长活动，负责数据分析和页面优化。

建议：
负责用户增长活动的数据分析与落地优化，
基于转化漏斗定位关键流失环节，
推动页面文案与转化路径调整。

依据：
- 简历原文：用户增长活动、数据分析、页面优化
- JD 要求：熟悉转化漏斗、增长策略、数据驱动

风险：
低风险。未新增项目事实，只强化已有表达。

[接受] [拒绝] [编辑]
```

这比"AI 一键改好简历"可信得多。

### 10.2 事实账本 (Fact Ledger)

所有 LLM 改写都必须引用 Fact。没有 Fact 支撑的内容不能进入最终简历。

从架构上防止：
- ❌ 把"了解 K8s"写成"主导 K8s 集群治理"
- ❌ 把"参与项目"写成"负责核心架构"
- ❌ 把公司价值观硬塞进自我评价

### 10.3 Policy Guard 安全策略

| 类别 | 示例 | 策略 |
|------|------|------|
| Allowed | 改写表达、调整顺序、强化已有事实 | 直接应用 |
| NeedsConfirmation | 数字化成果、技术深度提升、责任范围扩大 | 标记待确认 |
| Forbidden | 编造项目、编造指标、编造职责 | 拒绝 |

---

## 十一、商业化（v3）

### 11.1 免费层
- 1 次快速 JD 匹配
- 基础 Match Score
- 3 条修改建议
- 不可导出或带水印导出

### 11.2 单次付费
- ¥9.9-29.9 / 次
- 完整诊断 + diff + DOCX/PDF 导出
- 岗位版本保存 7 天

### 11.3 深度 Target Report
- ¥39-99 / 次
- 公司官网/App/JD 深度分析 + 多 JD 共性 + 简历策略 + 面试亮点

### 11.4 订阅
- ¥29-59 / 月
- 多岗位版本 + 不限次数基础优化 + 历史版本管理

### 11.5 B2B / 顾问版
- 高校就业指导 / 职业咨询师 / 简历服务工作室 / 求职训练营

**早期建议做"单次深度报告"而不是一上来做订阅。**

---

## 十二、推广角度

- "我做了一个不会编经历的 AI 简历医生"
- "不是简历生成器，是简历手术台"
- "针对字节/腾讯/阿里 JD，生成可审计的简历修改报告"
- "每处修改都有证据，不再让 AI 瞎编工作经历"
- "打开网页就能用，不需要装任何东西"

---

## 十三、风险评估

| 风险 | 等级 | 对策 |
|------|------|------|
| LLM 编造经历 | **高** | Fact Ledger + Policy Guard + evidence-based rewrite + diff + 用户确认 |
| 竞品同质化 | **高** | 主打证据化修改 + 公司理解 + 反幻觉 |
| Web 复杂度 | **中** | Next.js SSR + FastAPI，先做最小闭环 |
| 公司信息采集准确性 | **中** | 用户确认候选官网，不自动匹配 |
| DeepSeek/Kimi API 稳定性 | **中** | LiteLLM fallback 机制 |
| 用户付费意愿 | **中** | 先做单次报告验证 |
| 个人信息合规 | **中** | 24h 自动删除、一键删除、不训练承诺 |
| 开源传播减弱 | **低** | CLI 后置作为开源内核 |

---

*PLAN v3 — 基于 v3 可行性审查报告修订*
*最后更新: 2026-06-01*
*作者: 老大 + 露露緹婭*

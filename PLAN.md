# CV-Doctor 简历对症下药 — 项目方案 v2

> 隐私优先的 AI 简历诊断工具。不会替你编造经历，而是基于原始简历、目标 JD 和公开公司资料，生成可审计的修改建议、差距报告和针对性简历版本。

## 项目定位（v2 修订）

**一句话定位：** 面向中文求职的、隐私优先的、证据化简历"对症下药"工具。

**核心卖点：**
- 🇨🇳 中文精投：BOSS/拉勾/猎聘/牛客/天眼查等中国数据源组合
- 🔍 精投场景：同公司多 JD 交叉分析，不只是单条 JD 关键词匹配
- 📋 可审计修改：每一句优化都说明来自简历原文、JD、公司公开资料，还是用户确认补充
- 🔒 隐私优先：本地 LLM、BYO API Key、默认不上传、不留存
- 🛡️ 反幻觉：不编造经历，只改表达；缺失项只做"补充建议"，不偷偷写进简历

**不是什么：**
- 不是简历生成器（不从零建简历）
- 不是 ATS 评分器（没有统一真实 ATS 标准）
- 不是求职自动化平台（不自动投递、不打招呼）
- 不是"帮你骗过系统"的工具

---

## 一、调研结论（v2 修订）

### 1.1 竞品全景

| 项目 | Stars | 定位 | 关键差距 |
|------|-------|------|----------|
| **boss-agent-cli** | 979 | BOSS直聘 AI Agent（求职自动化） | 简历优化是附属功能，无公司深度分析 |
| **JadeAI** | 1.7k | 全能简历生成器（50+模板） | 生成器而非优化器，无公司分析 |
| **resume-lm** | 271 | AI 简历构建器 | 无公司分析，无中文优化 |
| **resume-builder-skill** | 22 | 中文 AI 简历 Skill | Agent Skill 形式，无独立运行能力 |
| **resume-tailoring-skill** | - | 海外公司研究型简历定制 | 已含公司文化、角色要求、技术博客研究，但无中文场景 |
| 商业工具 (Jobscan/Teal/Rezi) | - | ATS 匹配 + AI 改写 | 功能成熟但不开源，无本地隐私，无中文精投 |

### 1.2 市场空白（v2 修正）

> 原表述"没有任何开源项目做到公司深度分析"需要修正。
> 海外已有 resume-tailoring-skill 等项目做公司研究型简历定制。

**更准确的差异化：** 现有工具大多集中在简历生成、JD 关键词匹配和 ATS 格式优化；虽然海外已有少量项目开始做公司研究型简历定制，但在**中文求职场景、目标公司多源情报、同公司多 JD 交叉分析、隐私优先本地运行、可审计事实约束**方面，仍存在明显开源空白。

### 1.3 竞品缺口

现有工具解决的是"把简历改得像 JD"，而不是"帮候选人理解目标公司，并以证据化方式重排简历叙事"。

CV-Doctor 的 Target Mode 本质上是在做**求职研究 + 简历手术**，这比单纯的 ATS 分更有差异化。

---

## 二、核心功能设计（v2 修订）

### 2.1 两种模式

#### 模式一：通用诊断（Quick Mode）
```
输入：简历(Markdown/DOCX) + JD文本
输出：三件套（优化简历 + 手术报告 + 修改 diff）
```
- 关键词匹配分析
- 措辞优化（动词强化、量化数据）
- Match Score（不是 ATS 分）
- 适合：海投场景，快速优化

#### 模式二：对症下药（Target Mode）⭐ 核心卖点
```
输入：简历(Markdown/DOCX) + 目标公司名 + 目标岗位
输出：三件套 + 公司画像报告 + 面试可展开亮点
```
- 自动采集公司画像（官网、技术博客、GitHub）
- 用户导入多 JD（手动粘贴/文件导入）
- 同公司多 JD 交叉分析
- 公司文化匹配度分析
- 技术栈对齐建议
- 差距分析（匹配 / 部分匹配 / 缺失）
- 面试可展开亮点（原"面试引导点预埋"改名）
- 适合：精投场景，精准打击

### 2.2 三件套输出（v2 新增）

每次优化固定输出三份产物：

| 产物 | 说明 | 用户价值 |
|------|------|----------|
| `optimized_resume.md/docx` | 优化后简历 | 可直接投递或继续编辑 |
| `surgery_report.md` | 手术报告 | 解释为什么这样改，避免黑盒 |
| `changes.diff.md` | 修改 diff | 每处修改的原文、改文、依据、风险 |

`changes.diff.md` 是最重要的差异化：

```markdown
### 修改 3：项目经历排序

原文：
- A 项目：内部管理系统
- B 项目：高并发推荐服务

修改后：
- B 项目：高并发推荐服务
- A 项目：内部管理系统

依据：
- JD 必须项：高并发、推荐系统、Redis、消息队列
- 公司技术博客：近期多次提及推荐架构与实时特征

风险：
- 无事实新增，仅调整展示顺序
```

### 2.3 Match Score（v2 改名）

> 原"ATS Score"改为"Match Score / 投递匹配度"。
> 没有统一真实 ATS 标准，不应暗示这是招聘系统真实分数。

评分拆解为四项：

| 评分项 | 权重 | 说明 |
|--------|------|------|
| 必须项覆盖 | 40% | JD must-have 是否有简历证据 |
| 关键词覆盖 | 25% | 技能、工具、领域词覆盖 |
| 经历相关性 | 25% | 项目/工作经历是否能支持岗位要求 |
| 表达与格式 | 10% | 动词、量化、可读性、ATS 友好格式 |

### 2.4 功能清单（v2 修订）

| 功能 | Phase | 说明 |
|------|-------|------|
| Markdown 简历解析 | P0 | 一等公民，最稳 |
| JD 文本分析 | P0 | LLM 结构化提取 + 分类 |
| 证据化简历优化 | P0 | Fact-based rewrite，不编造 |
| 修改 diff 输出 | P0 | 每处修改有依据有风险 |
| 手术报告输出 | P0 | Match Score + 差距分析 |
| CLI 入口 | P0 | Typer 框架 |
| 本地 LLM 支持 | P0 | Ollama 集成 |
| DOCX 解析 | P1 | python-docx |
| 基础 PDF 文本解析 | P1 | PyMuPDF/pdfplumber（非 marker） |
| DOCX 输出 | P1 | python-docx |
| LiteLLM 完整封装 | P1 | 多提供商 + fallback |
| Match Score 固化 | P1 | 四维评分体系 |
| 变更审阅机制 | P1 | 逐条接受/拒绝 |
| 测试 fixtures | P1 | 样本简历 + JD |
| 用户导入多 JD | P2 | 手动粘贴/文件导入 |
| 公司官网/技术博客采集 | P2 | 公开资料，带来源和置信度 |
| 天眼查 optional provider | P2 | 不作为默认依赖 |
| 公司画像报告 | P2 | 证据化，每条带来源 |
| 技术栈与文化匹配 | P2 | Target Report |
| 面试可展开亮点 | P2 | 简历亮点解释稿 |
| Web 前端 | P3 | Next.js |
| 简历版本管理 | P3 | 多公司版本对比 |
| 模板系统 | P3 | HTML 模板 + WeasyPrint |
| Docker 一键部署 | P3 | docker-compose |
| BOSS 直聘 JD 采集 | P3* | *实验性插件，不作为核心卖点 |

---

## 三、技术架构（v2 修订）

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户输入层                          │
│  简历(MD/DOCX) + JD文本(粘贴/文件) + 目标公司(可选)       │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                    Evidence Store 证据库 ← v2 新增       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 简历事实  │  │ JD 要求  │  │ 公司情报  │              │
│  │ Facts    │  │ Reqs     │  │ Claims   │              │
│  │ 来源:简历 │  │ 来源:JD  │  │ 来源:公开 │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                   Policy Guard 安全策略 ← v2 新增        │
│  Allowed: 改写表达、调整顺序、强化已有事实               │
│  NeedsConfirm: 数字化成果、技术深度提升、责任范围扩大     │
│  Forbidden: 编造项目、编造指标、编造职责、暗示不存在经验   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      分析引擎层                          │
│  JD解析 | 差距分析 | Match Score | 公司画像(可选)        │
│           LiteLLM（统一接口，30+提供商）                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      优化输出层                          │
│  简历重写(证据化) | 手术报告 | 修改diff | Match Score    │
└─────────────────────────────────────────────────────────┘
```

### 3.2 技术栈选型（v2 修订）

| 模块 | 技术方案 | 理由 |
|------|----------|------|
| 语言 | Python 3.11+ | 生态最丰富，LLM 库最多 |
| CLI 框架 | Typer | 类型提示驱动，自动生成帮助文档 |
| Markdown 解析 | 一等公民 | 最稳，P0 默认格式 |
| DOCX 解析 | python-docx | 成熟稳定，MIT 许可 |
| PDF 解析 | PyMuPDF / pdfplumber | 宽松许可，P1 阶段引入 |
| PDF 高级解析 | marker-pdf [optional] | GPL-3.0，作为可选增强，不作硬依赖 |
| LLM 接口 | LiteLLM | 统一接口，支持 OpenAI/Ollama/Gemini/Claude |
| 结构化输出 | Pydantic v2 | JSON Schema 强类型校验 |
| PDF 生成 | WeasyPrint | HTML→PDF，P3 阶段引入 |
| DOCX 生成 | python-docx | 直接生成 Word，P1 阶段引入 |
| 网页采集 | httpx + readability | 公司官网/技术博客，轻量级 |
| 企业信息 | 天眼查 API [optional] | 不作为默认依赖 |
| 向量相似度 | scikit-learn | TF-IDF + 余弦相似度 |
| 本地 LLM | Ollama | 隐私优先，离线可用 |
| 测试 | pytest + fixtures | 样本简历 + JD |
| 包管理 | uv | 快速，兼容 pip |

### 3.3 LLM 接口设计（v2 新增）

> 不要一个大 prompt 一次性完成所有任务。拆成四个稳定接口：

```python
class LLMClient:
    """LLM 统一客户端 — 四个稳定接口"""

    def extract_resume(self, raw_text: str) -> ResumeDraft:
        """简历解析：原始文本 → 结构化 Resume"""

    def analyze_jd(self, jd_text: str) -> JobAnalysis:
        """JD 分析：JD 文本 → 结构化需求 + 关键词 + 权重"""

    def compare_resume_jd(self, resume: Resume, jd: JobAnalysis) -> GapReport:
        """差距分析：简历 vs JD → 匹配报告"""

    def rewrite_with_evidence(
        self,
        resume: Resume,
        gap_report: GapReport,
        evidence_store: EvidenceStore,
        constraints: PolicyGuard,
    ) -> ChangeSet:
        """证据化改写：基于证据库 + 安全策略 → 修改集"""
```

### 3.4 核心 Pipeline（v2 修订）

```
Step 1: 简历解析
  Markdown/DOCX → Pydantic Resume 模型
  同时提取 Fact（简历事实）→ Evidence Store

Step 2: JD 分析
  用户粘贴 JD 文本 / 文件导入
  LLM 结构化提取 → JobAnalysis 模型
  同时提取 Requirement → Evidence Store

Step 3: 公司画像采集（Target Mode 可选）
  公司官网 → {使命, 价值观, 产品}
  技术博客 → {技术栈, 技术方向}
  GitHub 组织 → {开源项目, 技术方向}
  每条 Claim 带来源 URL + 置信度 → Evidence Store
  ⚠️ 天眼查作为 optional provider，不作为默认依赖

Step 4: 差距分析
  Evidence Store 中的 Fact vs Requirement 逐条对比
  → 完全匹配项（强化关键词密度）
  → 部分匹配项（优化措辞使其更匹配）
  → 缺失项（仅做补充建议，不写入简历）

Step 5: 证据化简历优化 ← v2 核心改动
  Policy Guard 检查每条修改：
    Allowed → 直接改写
    NeedsConfirmation → 标记待用户确认
    Forbidden → 拒绝，不进入输出
  每条修改必须引用 evidence_ids
  输出 ChangeSet（原文 → 改后 → 依据 → 风险）

Step 6: Match Score 计算
  四维评分：必须项覆盖(40%) + 关键词覆盖(25%)
           + 经历相关性(25%) + 表达格式(10%)
  优化前 vs 优化后对比

Step 7: 三件套输出
  ① optimized_resume.md/docx — 优化后简历
  ② surgery_report.md — 手术报告（为什么改）
  ③ changes.diff.md — 修改 diff（原文/改文/依据/风险）
```

---

## 四、数据模型设计（v2 修订）

### 4.1 核心模型

```python
from pydantic import BaseModel
from enum import Enum
from typing import Literal

# ==================== 证据系统（v2 新增）====================

class FactSource(str, Enum):
    RESUME = "resume"           # 来自用户简历
    USER_INPUT = "user_input"   # 来自用户手动输入
    JD = "jd"                   # 来自 JD 文本
    COMPANY = "company_source"  # 来自公司公开资料

class Fact(BaseModel):
    """事实账本 — 所有可用证据"""
    id: str
    text: str
    source: FactSource
    source_url: str = ""        # 来源链接（公司资料必填）
    confidence: float = 1.0     # 置信度 0-1
    can_use_in_resume: bool = True
    requires_user_confirmation: bool = False

class EvidenceStore(BaseModel):
    """证据库"""
    facts: list[Fact] = []

    def add(self, fact: Fact) -> None:
        self.facts.append(fact)

    def get_by_source(self, source: FactSource) -> list[Fact]:
        return [f for f in self.facts if f.source == source]

    def get_usable(self) -> list[Fact]:
        return [f for f in self.facts if f.can_use_in_resume]

# ==================== 安全策略（v2 新增）====================

class ChangeRisk(str, Enum):
    LOW = "low"           # 改写表达、调整顺序
    MEDIUM = "medium"     # 数字化成果、技术深度提升
    HIGH = "high"         # 责任范围扩大、新技能加入

class PolicyAction(str, Enum):
    ALLOWED = "allowed"
    NEEDS_CONFIRMATION = "needs_confirmation"
    FORBIDDEN = "forbidden"

class PolicyGuard(BaseModel):
    """安全策略 — 控制哪些内容能写进简历"""

    def check_change(self, change: "Change") -> PolicyAction:
        """检查一条修改是否允许"""
        if change.risk_level == ChangeRisk.LOW:
            return PolicyAction.ALLOWED
        elif change.risk_level == ChangeRisk.MEDIUM:
            return PolicyAction.NEEDS_CONFIRMATION
        else:
            return PolicyAction.NEEDS_CONFIRMATION

# ==================== 修改记录（v2 增强）====================

class Change(BaseModel):
    """单条修改记录 — v2 增加证据链"""
    section: str                        # e.g., "experiences[0].achievements[1]"
    original: str                       # 原文
    revised: str                        # 改后
    reason: str                         # 修改原因
    evidence_ids: list[str] = []        # 引用的 Fact ID
    risk_level: ChangeRisk = ChangeRisk.LOW
    requires_user_confirmation: bool = False
    source_label: str = ""              # "来自JD第3条" / "来自公司技术博客"

class ChangeSet(BaseModel):
    """修改集"""
    changes: list[Change] = []

    @property
    def confirmed_changes(self) -> list[Change]:
        return [c for c in self.changes if not c.requires_user_confirmation]

    @property
    def pending_changes(self) -> list[Change]:
        return [c for c in self.changes if c.requires_user_confirmation]

# ==================== Match Score（v2 改名）====================

class MatchScore(BaseModel):
    """投递匹配度（原 ATS Score）"""
    overall: float = 0.0            # 总分 0-100
    mandatory_coverage: float = 0.0 # 必须项覆盖 40%
    keyword_coverage: float = 0.0   # 关键词覆盖 25%
    experience_relevance: float = 0.0 # 经历相关性 25%
    expression_quality: float = 0.0 # 表达与格式 10%

# ==================== 原有模型（保留，微调）====================

class ContactInfo(BaseModel):
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    location: str = ""

class Experience(BaseModel):
    company: str
    title: str
    duration: str = ""
    location: str = ""
    description: str = ""
    achievements: list[str] = []
    keywords: list[str] = []

class Education(BaseModel):
    school: str
    degree: str = ""
    major: str = ""
    duration: str = ""
    gpa: str = ""
    highlights: list[str] = []

class Project(BaseModel):
    name: str
    role: str = ""
    duration: str = ""
    description: str = ""
    tech_stack: list[str] = []
    achievements: list[str] = []
    keywords: list[str] = []

class Resume(BaseModel):
    name: str
    contact: ContactInfo = ContactInfo()
    summary: str = ""
    experiences: list[Experience] = []
    education: list[Education] = []
    skills: list[str] = []
    projects: list[Project] = []
    certifications: list[str] = []
    languages: list[str] = []
    raw_text: str = ""

class JobRequirement(BaseModel):
    text: str
    category: str           # hard_skill / soft_skill / experience / education
    is_mandatory: bool = True
    weight: float = 0.5     # 0-1
    match_level: str = "missing"  # full / partial / missing
    resume_evidence: str = ""

class JobDescription(BaseModel):
    title: str
    company: str
    location: str = ""
    salary_range: str = ""
    description: str = ""
    requirements: list[JobRequirement] = []
    keywords: list[str] = []
    hard_skills: list[str] = []
    soft_skills: list[str] = []

class CompanyClaim(BaseModel):
    """公司情报（v2 新增 — 每条带来源）"""
    claim: str
    source_type: str        # tech_blog / official_site / github / news
    source_url: str = ""
    collected_at: str = ""
    confidence: float = 0.5

class CompanyProfile(BaseModel):
    name: str
    industry: str = ""
    size: str = ""
    funding_stage: str = ""
    founded: str = ""
    headquarters: str = ""
    website: str = ""
    description: str = ""
    culture_keywords: list[str] = []
    values: list[str] = []
    tech_stack: list[str] = []
    claims: list[CompanyClaim] = []     # v2: 证据化公司情报
    interview_insights: list[str] = []

class GapReport(BaseModel):
    """差距分析报告"""
    match_score: MatchScore = MatchScore()
    requirements_analysis: list[JobRequirement] = []
    strengths: list[str] = []
    gaps: list[str] = []
    suggestions: list[str] = []

class SurgeryReport(BaseModel):
    """手术报告（v2 新增）"""
    match_score_before: MatchScore
    match_score_after: MatchScore
    score_improvement: float = 0.0
    gap_report: GapReport
    company_profile: CompanyProfile | None = None
    interview_highlights: list[str] = []    # 面试可展开亮点
    changes_summary: str = ""

class OptimizationResult(BaseModel):
    """优化结果 — v2 三件套"""
    original_resume: Resume
    optimized_resume: Resume
    changeset: ChangeSet                    # 修改 diff
    surgery_report: SurgeryReport           # 手术报告
    evidence_store: EvidenceStore           # 证据库（可选输出）
```

---

## 五、项目结构（v2 修订）

```
cv-doctor/
├── PLAN.md                 # 本文档
├── README.md               # 项目说明
├── pyproject.toml          # 项目配置 + 依赖
├── LICENSE                 # MIT
├── .env.example            # 环境变量示例
│
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口（Typer）
│   ├── config.py           # 配置管理
│   ├── models.py           # Pydantic 数据模型
│   │
│   ├── parser/             # 简历解析模块
│   │   ├── __init__.py
│   │   ├── md_parser.py    # Markdown 解析 ← P0 一等公民
│   │   ├── docx_parser.py  # DOCX 解析 ← P1
│   │   ├── pdf_parser.py   # PDF 解析（PyMuPDF）← P1
│   │   └── normalizer.py   # 统一输出 Resume 模型
│   │
│   ├── evidence/           # 证据系统（v2 新增）
│   │   ├── __init__.py
│   │   ├── store.py        # Evidence Store
│   │   ├── fact_extractor.py # 从简历/JD/公司资料提取 Fact
│   │   └── policy.py       # Policy Guard 安全策略
│   │
│   ├── analyzer/           # 分析引擎
│   │   ├── __init__.py
│   │   ├── jd_analyzer.py      # JD 关键词提取 + 分类
│   │   ├── gap_analyzer.py     # Fact vs Requirement 差距分析
│   │   ├── match_scorer.py     # Match Score（四维评分）
│   │   └── company_analyzer.py # 公司画像分析（P2）
│   │
│   ├── optimizer/          # 优化引擎
│   │   ├── __init__.py
│   │   └── resume_optimizer.py # 证据化简历优化（核心）
│   │
│   ├── output/             # 输出模块
│   │   ├── __init__.py
│   │   ├── md_generator.py     # Markdown 输出 ← P0
│   │   ├── docx_generator.py   # DOCX 输出 ← P1
│   │   ├── pdf_generator.py    # PDF 输出 ← P3
│   │   ├── surgery_report.py   # 手术报告生成 ← P0
│   │   └── changes_diff.py     # 修改 diff 生成 ← P0
│   │
│   ├── collectors/         # 数据采集模块（P2/P3）
│   │   ├── __init__.py
│   │   ├── website_collector.py # 公司官网/技术博客 ← P2
│   │   ├── github_collector.py  # GitHub 组织 ← P2
│   │   └── boss_collector.py    # BOSS 直聘 ← P3 实验性插件
│   │
│   └── llm/                # LLM 接口封装
│       ├── __init__.py
│       ├── client.py           # 四接口客户端
│       ├── prompts.py          # Prompt 模板管理
│       └── structured_output.py# 结构化输出 + JSON 修复
│
├── prompts/                # Prompt 模板文件
│   ├── extract_resume.md       # 简历解析
│   ├── analyze_jd.md           # JD 分析
│   ├── compare_gap.md          # 差距分析
│   ├── rewrite_evidence.md     # 证据化改写
│   └── match_score.md          # Match Score
│
├── tests/
│   ├── test_parser.py
│   ├── test_evidence.py
│   ├── test_analyzer.py
│   ├── test_optimizer.py
│   ├── test_policy.py
│   └── fixtures/           # 测试用样本
│       ├── sample_resume.md
│       ├── sample_resume.docx
│       └── sample_jd.txt
│
└── docs/
    ├── architecture.md
    ├── evidence_system.md  # 证据系统文档
    └── contributing.md
```

---

## 六、CLI 设计（v2 修订）

### 6.1 命令结构

```bash
# ========== P0: 通用诊断 ==========
cv-doctor diagnose resume.md --jd-file jd.txt
# 输出：三件套（优化简历 + 手术报告 + 修改 diff）

# ========== P1: 增强诊断 ==========
cv-doctor diagnose resume.docx --jd-file jd.txt --format docx
cv-doctor diagnose resume.pdf --jd "岗位描述..."

# ========== P2: 对症下药 ==========
cv-doctor target resume.md --company "字节跳动" --position "后端开发"
cv-doctor target resume.md --company "腾讯" --position "产品经理" --city "深圳"

# ========== P2: 独立功能 ==========
cv-doctor company "字节跳动"                    # 公司画像
cv-doctor import-jd --from-file jd.txt          # 导入 JD
cv-doctor import-jd --from-text "..."           # 粘贴 JD

# ========== 通用 ==========
cv-doctor parse resume.md                       # 简历解析（调试）
cv-doctor config set llm.provider ollama        # 配置
```

### 6.2 输出示例（v2 修订）

```
$ cv-doctor diagnose resume.md --jd-file jd.txt

━━━ CV-Doctor 简历诊断 ━━━

📋 简历解析完成
   姓名: 张三 | 工作经验: 5年 | 技能: 12项
   提取事实: 23 条（来自简历原文）

📊 JD 分析
   硬技能: Go(必须), K8s(必须), 分布式系统(必须), MySQL(加分)
   软技能: 沟通能力, 自驱力

🔍 差距分析
   ✅ 完全匹配 (5/8): Go, MySQL, 微服务架构, RESTful API, Git
   ⚠️ 部分匹配 (2/8): K8s(有Docker经验但未提及K8s), 分布式(有概念但缺实践)
   ❌ 缺失 (1/8): Rust → 仅做补充建议，不写入简历

📝 修改集 (7 条修改)
   ✅ 直接应用: 5 条（改写表达、调整顺序）
   ⏳ 待确认:   2 条（技术深度提升，需用户确认）
   🚫 已拒绝:   0 条

📈 Match Score
   优化前: 62/100 (必须项: 55% | 关键词: 58% | 相关性: 70% | 表达: 65%)
   优化后: 85/100 (必须项: 88% | 关键词: 91% | 相关性: 82% | 表达: 78%)
   提升: +23 分

✅ 输出三件套:
   📄 优化简历:      output/张三_optimized_resume.md
   📋 手术报告:      output/张三_surgery_report.md
   📝 修改 diff:     output/张三_changes.diff.md
```

---

## 七、实施路线（v2 大幅修订）

### P0: 验证版 — 1-2 周
> 目标：证明"比直接问 ChatGPT 更可信"

**范围：**
```
cv-doctor diagnose resume.md --jd-file jd.txt
```

**交付：**
- [ ] Markdown 简历输入
- [ ] JD 文本输入（文件或粘贴）
- [ ] JD requirements 结构化（Pydantic）
- [ ] 简历 Fact 提取 → Evidence Store
- [ ] 差距分析（Gap Report）
- [ ] 修改 diff（ChangeSet，每条有依据有风险）
- [ ] 优化后 Markdown 简历
- [ ] 手术报告（Match Score + 差距 + 修改摘要）
- [ ] 四接口 LLM 客户端（extract / analyze / compare / rewrite）
- [ ] Policy Guard 基础版
- [ ] 本地 Ollama 或 BYO API Key
- [ ] 基础测试

**暂不做：** PDF 解析、DOCX 输出、BOSS 采集、天眼查、Web 前端、模板系统

**验收标准：**

| 指标 | 目标 |
|------|------|
| 事实新增率 | 0：没有证据的内容不能进入简历 |
| 输出可读性 | 人能直接理解每处修改原因 |
| JD 必须项识别 | 能稳定区分 must-have / nice-to-have |
| 运行方式 | 一个命令跑通 |
| 对比 ChatGPT | 用户认为报告更可信、更好改 |

### P1: 可用 CLI — 4-6 周
> 目标：生产可用的诊断工具

- [ ] DOCX 解析
- [ ] 基础 PDF 文本解析（PyMuPDF，非 marker）
- [ ] DOCX 输出
- [ ] LiteLLM 完整封装（fallback、重试）
- [ ] Match Score 四维评分固化
- [ ] 变更审阅机制（逐条接受/拒绝）
- [ ] 测试 fixtures（样本简历 + JD）
- [ ] README 完善（安装、使用、示例）
- [ ] 本地缓存（避免重复 LLM 调用）

### P2: 对症下药 — 6-8 周
> 目标：Target Mode 可用

- [ ] 公司官网/技术博客采集（httpx + readability）
- [ ] GitHub 组织分析
- [ ] 用户手动导入多 JD
- [ ] 天眼查 optional provider（不作为默认依赖）
- [ ] 公司画像报告（每条带来源 + 置信度）
- [ ] 技术栈匹配
- [ ] 文化/表达风格建议
- [ ] 面试可展开亮点

**⚠️ BOSS 直聘采集不放在 P2 主线。**
JD 导入方式：
```bash
cv-doctor import-jd --from-file jd.txt
cv-doctor import-jd --from-text "..."
cv-doctor import-jd --from-browser  # 用户主动打开页面，本地提取（谨慎）
```

### P3: Web/桌面端 — 8-10 周+
> 目标：用户体验完善

- [ ] Web 前端（Next.js）
- [ ] 简历版本管理（多公司版本对比）
- [ ] 逐条接受/拒绝 UI
- [ ] 模板系统（HTML + WeasyPrint）
- [ ] PDF 输出
- [ ] Docker 一键部署
- [ ] 历史记录
- [ ] BOSS 直聘采集（实验性插件）

---

## 八、关键设计决策（v2 修订）

### 8.1 证据化修改（v2 核心改动）

> 架构级防幻觉，不只是 Prompt 约束。

**事实账本 (Fact Ledger)：**
- 简历解析时自动提取 Fact（每段经历、每个技能、每个成就）
- JD 分析时提取 Requirement
- 公司采集时提取 Claim（每条带来源 URL + 置信度）
- 所有 LLM 改写都必须引用 evidence_ids
- 没有 Fact 支撑的内容不能进入最终简历

**Policy Guard 安全策略：**

| 类别 | 示例 | 策略 |
|------|------|------|
| Allowed | 改写表达、调整顺序、强化已有事实、映射 JD 关键词 | 直接应用 |
| NeedsConfirmation | 数字化成果、技术深度提升、责任范围扩大、新技能加入 | 标记待确认 |
| Forbidden | 编造项目、编造指标、编造职责、暗示不存在经验 | 拒绝，不进入输出 |

**从架构上防止：**
- ❌ 把"了解 K8s"写成"主导 K8s 集群治理"
- ❌ 把"参与项目"写成"负责核心架构"
- ❌ 把"使用 Redis"写成"设计高可用缓存体系"
- ❌ 把公司价值观硬塞进自我评价

### 8.2 隐私保护

1. **本地优先**：默认支持 Ollama，简历数据不出本机
2. **无服务器模式**：纯 CLI，不需要后端服务
3. **数据不持久化**：除非用户明确要求，否则不保存简历内容
4. **透明日志**：所有 LLM 调用的输入输出可查看
5. **BYO API Key**：用户自带密钥，不经过第三方

### 8.3 合规设计

1. **JD 采集**：默认手动粘贴/文件导入；浏览器提取为用户主动操作
2. **BOSS 直聘**：不作为核心功能，最多作为实验性插件；不宣传反检测
3. **天眼查**：不作为默认依赖；用户自行申请 API Key
4. **个人信息**：简历数据默认不上传、不留存、不持久化
5. **marker-pdf**：GPL-3.0，作为 optional extra；README 明确许可说明

---

## 九、风险评估（v2 修订）

| 风险 | 等级 | 对策 |
|------|------|------|
| LLM 编造经历 | **高** | Fact Ledger + Policy Guard + evidence-based rewrite + diff + 用户确认 |
| 招聘平台采集合规 | **高** | 默认手动粘贴；BOSS 采集做成实验插件；不宣传反检测 |
| 竞品同质化 | **高** | 主打中文精投、公司画像、证据链、本地隐私 |
| marker 许可风险 | **中高** | 作为 optional extra；默认用宽松许可解析器 |
| PDF 解析不稳定 | **中** | Markdown/DOCX 优先；PDF 做 parse confidence |
| Match Score 可信度 | **中** | 四维评分拆解依据；不叫 ATS 分 |
| 公司画像噪声 | **中** | 每条必须带来源和置信度 |
| 本地 LLM 效果不稳 | **中** | 默认推荐云模型；本地模式降低功能承诺 |
| 开源维护成本 | **中** | 先支持少量输入格式；用 fixtures 收敛 bug |

---

## 十、商业化与开源策略（v2 新增）

### 10.1 开源定位

README 首屏：
> CV-Doctor 是一个隐私优先的 AI 简历诊断工具。
> 它不会替你编造经历，而是基于你的原始简历、目标 JD 和公开公司资料，
> 生成可审计的修改建议、差距报告和针对性简历版本。

### 10.2 开源 vs 付费

| 层级 | 功能 |
|------|------|
| 开源 CLI | 本地简历诊断、JD 分析、MD/DOCX 输出、BYO Key、本地 Ollama |
| Pro/桌面端 | 更好模板、批量岗位版本、历史对比、本地知识库 |
| SaaS | Web 编辑器、协作、版本管理、云端模型 |
| B2B/顾问版 | 多候选人管理、报告模板、顾问工作台 |
| 数据增强 | 天眼查/企业画像/行业词库作为可选增值 |

### 10.3 推广角度

- "我做了一个不会编经历的 AI 简历医生"
- "不是简历生成器，是简历手术台"
- "针对字节/腾讯/阿里 JD，生成可审计的简历修改报告"
- "本地运行，简历不出电脑"
- "每处修改都有证据，不再让 AI 瞎编工作经历"

---

*PLAN v2 — 基于外部可行性审查报告修订*
*最后更新: 2026-06-01*
*作者: 老大 + 露露緹婭*

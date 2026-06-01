# CV-Doctor 简历对症下药 — 项目方案

> LLM 驱动的简历深度优化工具，针对具体公司+岗位精准优化简历

## 项目愿景

做一个开源的、隐私优先的简历优化工具。不同于市面上的"简历生成器"，CV-Doctor 的核心定位是**简历优化器**——你已有简历，我们帮你针对目标公司和岗位"对症下药"。

---

## 一、调研结论

### 1.1 竞品全景

| 项目 | Stars | 定位 | 最后更新 | 关键差距 |
|------|-------|------|----------|----------|
| **boss-agent-cli** | 979 | BOSS直聘 AI Agent（求职自动化） | 5天前 | 简历优化是附属功能，无公司深度分析 |
| **JadeAI** | 1.7k | 全能简历生成器（50+模板） | 4小时前 | 生成器而非优化器，无公司分析 |
| **resume-lm** | 271 | AI 简历构建器 | 3周前 | 无公司分析，无中文优化 |
| **resume-builder-skill** | 22 | 中文 AI 简历 Skill | 2个月前 | Agent Skill 形式，无独立运行能力 |
| **AutoATS** | 63 | ATS 优化简历生成 | - | 无公司级分析 |
| **JeevansSP/resume-optimizer** | 33 | PDF→JD→ATS简历 | 2个月前 | 代码量小，无公司分析 |
| **Resume-Tailor-AI** | 29 | JD匹配+ATS关键词 | - | 无公司分析 |

### 1.2 市场空白

**没有任何开源项目做到「深度分析目标公司 → 针对性优化简历」这一层。**

现有工具停留在：
- 简历从零生成（生成器）
- JD 关键词匹配（浅层优化）
- ATS 格式检查（格式层面）

没有人做：
- 公司文化画像 → 简历风格调整
- 公司技术栈分析 → 项目经历优先级排序
- 同公司多 JD 交叉分析 → 提取隐性要求
- 面试情报 → 简历预埋面试引导点

### 1.3 差异化定位

```
boss-agent-cli = 求职自动化平台（投递、打招呼、收简历）
JadeAI         = 简历生成器（从零建简历）
CV-Doctor      = 简历深度优化专家（对症下药）
```

---

## 二、核心功能设计

### 2.1 两种模式

#### 模式一：通用优化（Quick Mode）
```
输入：简历(PDF/DOCX/MD) + JD文本
输出：优化后简历 + ATS评分 + 修改建议
```
- 关键词匹配分析
- 措辞优化（动词强化、量化数据）
- ATS 格式检查
- 适合：海投场景，快速优化

#### 模式二：对症下药（Target Mode）⭐ 核心卖点
```
输入：简历(PDF/DOCX/MD) + 目标公司名 + 目标岗位
输出：针对性优化简历 + 公司匹配报告 + 面试准备建议
```
- 自动采集公司画像（官网、技术博客、天眼查）
- 自动采集目标岗位 JD（BOSS直聘/拉勾/猎聘）
- 同公司多 JD 交叉分析
- 公司文化匹配度分析
- 技术栈对齐建议
- 差距分析（匹配 / 部分匹配 / 缺失）
- 面试引导点预埋
- 适合：精投场景，精准打击

### 2.2 功能清单

| 功能 | Phase | 说明 |
|------|-------|------|
| 简历解析（PDF/DOCX/MD） | P1 | marker-pdf + python-docx |
| JD 文本分析 | P1 | LLM 关键词提取 + 权重排序 |
| 简历优化（LLM驱动） | P1 | 多轮优化，保持事实准确 |
| ATS 评分 | P1 | TF-IDF 余弦相似度 + LLM 语义打分 |
| 多格式输出 | P1 | PDF / DOCX / Markdown |
| CLI 入口 | P1 | Typer 框架 |
| 本地 LLM 支持 | P1 | Ollama 集成 |
| 公司画像采集 | P2 | 天眼查API + 官网爬取 |
| BOSS直聘 JD 采集 | P2 | Playwright，参考 boss-agent-cli |
| 同公司多 JD 交叉分析 | P2 | 提取共性要求 |
| 公司文化匹配 | P2 | 从官网/博客/评价提取 |
| 技术栈对齐 | P2 | JD + 技术博客 + GitHub |
| 面试情报采集 | P3 | 牛客网/LeetCode 面经 |
| 面试引导点预埋 | P3 | 在简历中自然植入面试话题 |
| Web 前端 | P3 | Next.js（老大的强项） |
| Docker 一键部署 | P3 | docker-compose |

---

## 三、技术架构

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户输入层                          │
│  简历(PDF/DOCX/MD) + JD文本 / 目标公司+岗位              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      数据采集层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 简历解析  │  │ JD采集    │  │ 公司画像  │              │
│  │ marker-pdf│  │ Playwright│  │ 爬虫/API │              │
│  │ docx2txt │  │ 手动粘贴  │  │ 天眼查   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      分析引擎层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ JD解析    │  │ 公司画像  │  │ 差距分析  │              │
│  │ 关键词    │  │ 文化匹配  │  │ 优化建议  │              │
│  │ 权重排序  │  │ 技术栈    │  │ 评分系统  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│           LiteLLM（统一接口，30+提供商）                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      优化输出层                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │ 简历重写  │  │ 评分报告  │  │ 多格式   │              │
│  │ LLM优化  │  │ 匹配度   │  │ PDF/DOCX │              │
│  │ 事实保持  │  │ 差距分析  │  │ Markdown │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
```

### 3.2 技术栈选型

| 模块 | 技术方案 | 理由 |
|------|----------|------|
| 语言 | Python 3.11+ | 生态最丰富，LLM 库最多 |
| CLI 框架 | Typer | 类型提示驱动，自动生成帮助文档 |
| PDF 解析 | marker-pdf | ML 级 PDF 解析，表格/图片识别准确 |
| DOCX 解析 | python-docx | 成熟稳定 |
| LLM 接口 | LiteLLM | 统一接口，支持 OpenAI/Ollama/Gemini/Claude |
| 结构化输出 | Pydantic v2 | JSON Schema 强类型校验 |
| PDF 生成 | WeasyPrint | HTML→PDF，支持中文，比 LaTeX 轻量 |
| DOCX 生成 | python-docx | 直接生成 Word |
| 网页采集 | Playwright | 参考 boss-agent-cli，反检测能力强 |
| 企业信息 | 天眼查开放API | 工商信息、融资、规模 |
| 向量相似度 | scikit-learn | TF-IDF + 余弦相似度计算 ATS 分 |
| 本地 LLM | Ollama | 隐私优先，离线可用 |
| 测试 | pytest | 标准选择 |
| 包管理 | uv | 快速，兼容 pip |

### 3.3 核心 Pipeline（对症下药模式）

```
Step 1: 简历解析
  PDF/DOCX/MD → Pydantic Resume 模型
  {name, contact, summary, experience[], education[], skills[], projects[]}

Step 2: JD 采集
  方式A: 用户粘贴 JD 文本
  方式B: 自动从 BOSS直聘采集（需登录态）
  → Pydantic JobDescription 模型

Step 3: 公司画像采集（Target Mode 独有）
  天眼查 API → {行业, 规模, 融资, 成立时间}
  公司官网 → {使命, 价值观, 产品}
  技术博客 → {技术栈, 技术方向}
  → Pydantic CompanyProfile 模型

Step 4: JD 深度分析
  LLM 提取 → {硬技能[], 软技能[], 必须项[], 加分项[], 权重{}}
  同公司多 JD 交叉 → 共性要求 vs 个性要求

Step 5: 差距分析
  简历 vs JD 逐条对比
  → 完全匹配项（强化关键词密度）
  → 部分匹配项（优化措辞使其更匹配）
  → 缺失项（建议补充 / 诚实标注）

Step 6: 简历优化
  LLM 逐段优化（保持事实准确，只优化表述）
  公司文化匹配（调整语气和风格）
  技术栈对齐（优先展示匹配项目）
  面试引导点预埋（植入可展开的话题）

Step 7: 评分报告
  优化前 ATS 分 vs 优化后 ATS 分
  关键词覆盖率
  公司文化匹配度
  技术栈匹配度
  详细差距报告

Step 8: 多格式输出
  优化后简历 → PDF / DOCX / Markdown
  匹配报告 → Markdown / PDF
```

---

## 四、数据模型设计

### 4.1 核心 Pydantic 模型

```python
from pydantic import BaseModel
from enum import Enum

class MatchLevel(str, Enum):
    FULL = "full"           # 完全匹配
    PARTIAL = "partial"     # 部分匹配
    MISSING = "missing"     # 缺失

class ResumeSection(BaseModel):
    """简历中的一个段落/条目"""
    content: str
    keywords: list[str]
    relevance_score: float  # 与目标岗位的相关性 0-1

class Experience(BaseModel):
    company: str
    title: str
    duration: str
    description: str
    achievements: list[str]
    keywords: list[str]

class Resume(BaseModel):
    name: str
    contact: dict  # email, phone, linkedin, github, etc.
    summary: str
    experiences: list[Experience]
    education: list[dict]
    skills: list[str]
    projects: list[dict]
    certifications: list[str] = []

class JobRequirement(BaseModel):
    """JD 中的一条要求"""
    text: str
    category: str       # hard_skill / soft_skill / experience / education
    is_mandatory: bool  # 必须项 vs 加分项
    weight: float       # 重要程度 0-1
    match_level: MatchLevel = MatchLevel.MISSING
    resume_evidence: str = ""  # 简历中的对应证据

class JobDescription(BaseModel):
    title: str
    company: str
    location: str
    salary_range: str = ""
    description: str
    requirements: list[JobRequirement]
    keywords: list[str]

class CompanyProfile(BaseModel):
    """公司画像"""
    name: str
    industry: str
    size: str           # 1000-5000人 等
    funding_stage: str  # C轮、上市 等
    founded: str
    culture_keywords: list[str]     # 从官网/评价提取
    tech_stack: list[str]           # 从JD/博客/GitHub提取
    values: list[str]               # 企业价值观
    interview_insights: list[str]   # 面试特点

class MatchReport(BaseModel):
    """匹配度报告"""
    overall_score: float            # 总分 0-100
    keyword_coverage: float         # 关键词覆盖率
    culture_fit: float              # 文化匹配度
    tech_stack_match: float         # 技术栈匹配度
    requirements: list[JobRequirement]  # 逐条分析
    strengths: list[str]            # 优势项
    gaps: list[str]                 # 差距项
    suggestions: list[str]          # 优化建议

class OptimizationResult(BaseModel):
    """优化结果"""
    original_resume: Resume
    optimized_resume: Resume
    original_score: MatchReport
    optimized_score: MatchReport
    changes: list[dict]             # 修改明细
    company_profile: CompanyProfile | None  # Target Mode 独有
```

---

## 五、项目结构

```
cv-doctor/
├── PLAN.md                 # 本文档
├── README.md               # 项目说明（开源门面）
├── pyproject.toml          # 项目配置 + 依赖
├── LICENSE                 # MIT
├── .env.example            # 环境变量示例
├── docker-compose.yml      # Docker 部署
├── Dockerfile
│
├── src/
│   ├── __init__.py
│   ├── cli.py              # CLI 入口（Typer）
│   ├── config.py           # 配置管理
│   ├── models.py           # Pydantic 数据模型
│   │
│   ├── parser/             # 简历解析模块
│   │   ├── __init__.py
│   │   ├── pdf_parser.py   # PDF 解析（marker-pdf）
│   │   ├── docx_parser.py  # DOCX 解析
│   │   ├── md_parser.py    # Markdown 解析
│   │   └── resume_normalizer.py  # 统一输出 Resume 模型
│   │
│   ├── analyzer/           # 分析引擎
│   │   ├── __init__.py
│   │   ├── jd_analyzer.py      # JD 关键词提取 + 分类
│   │   ├── gap_analyzer.py     # 简历 vs JD 差距分析
│   │   ├── ats_scorer.py       # ATS 评分（TF-IDF + LLM）
│   │   ├── company_analyzer.py # 公司画像分析
│   │   └── culture_matcher.py  # 文化匹配分析
│   │
│   ├── optimizer/          # 优化引擎
│   │   ├── __init__.py
│   │   ├── resume_optimizer.py # LLM 驱动简历优化
│   │   ├── keyword_optimizer.py# 关键词密度优化
│   │   └── tone_adapter.py     # 语气风格适配
│   │
│   ├── output/             # 输出模块
│   │   ├── __init__.py
│   │   ├── pdf_generator.py    # PDF 生成
│   │   ├── docx_generator.py   # DOCX 生成
│   │   ├── md_generator.py     # Markdown 生成
│   │   └── report_generator.py # 匹配报告生成
│   │
│   ├── collectors/         # 数据采集模块（P2/P3）
│   │   ├── __init__.py
│   │   ├── boss_collector.py   # BOSS直聘 JD 采集
│   │   ├── company_collector.py# 公司信息采集
│   │   └── interview_collector.py# 面试情报采集
│   │
│   └── llm/                # LLM 接口封装
│       ├── __init__.py
│       ├── client.py           # LiteLLM 统一客户端
│       ├── prompts.py          # Prompt 模板管理
│       └── structured_output.py# 结构化输出解析
│
├── prompts/                # Prompt 模板文件
│   ├── jd_analysis.md
│   ├── gap_analysis.md
│   ├── resume_optimize.md
│   ├── company_profile.md
│   ├── culture_match.md
│   └── ats_score.md
│
├── templates/              # 简历模板
│   ├── classic.html
│   ├── modern.html
│   └── minimal.html
│
├── tests/
│   ├── test_parser.py
│   ├── test_analyzer.py
│   ├── test_optimizer.py
│   └── fixtures/           # 测试用简历样本
│       ├── sample_resume.pdf
│       ├── sample_resume.docx
│       └── sample_jd.txt
│
└── docs/
    ├── architecture.md     # 架构文档
    ├── api.md              # API 文档
    └── contributing.md     # 贡献指南
```

---

## 六、CLI 设计

### 6.1 命令结构

```bash
# 通用优化模式
cv-doctor optimize resume.pdf --jd "岗位描述文本..."
cv-doctor optimize resume.pdf --jd-file jd.txt
cv-doctor optimize resume.pdf --jd-url "https://www.zhipin.com/job_detail/..."

# 对症下药模式 ⭐
cv-doctor target resume.pdf --company "字节跳动" --position "后端开发工程师"
cv-doctor target resume.pdf --company "腾讯" --position "产品经理" --city "深圳"

# ATS 评分
cv-doctor score resume.pdf --jd "岗位描述文本..."

# 公司画像（独立查看）
cv-doctor company "字节跳动"
cv-doctor company "阿里巴巴" --position "前端开发"

# 简历解析（调试用）
cv-doctor parse resume.pdf
cv-doctor parse resume.docx --format json

# 配置管理
cv-doctor config set llm.provider openai
cv-doctor config set llm.model gpt-4o
cv-doctor config set llm.provider ollama  # 本地模式
cv-doctor config set llm.model llama3.1
```

### 6.2 输出示例

```
$ cv-doctor target resume.pdf --company "字节跳动" --position "后端开发"

━━━ CV-Doctor 简历对症下药 ━━━

📋 简历解析完成
   姓名: 张三 | 工作经验: 5年 | 技能: 12项

🏢 公司画像: 字节跳动
   行业: 互联网/信息技术 | 规模: 100000+人 | 阶段: 已上市
   文化关键词: 追求极致、开放谦逊、坦诚清晰、始终创业
   技术栈: Go, Rust, K8s, Microservice, Distributed System

📊 JD 分析 (基于 3 条同岗位 JD 交叉分析)
   硬技能: Go(必须), K8s(必须), 分布式系统(必须), MySQL(加分)
   软技能: 沟通能力, 自驱力, 技术热情

🔍 差距分析
   ✅ 完全匹配 (5/8): Go, MySQL, 微服务架构, RESTful API, Git
   ⚠️ 部分匹配 (2/8): K8s(有Docker经验但未提及K8s), 分布式(有概念但缺实践)
   ❌ 缺失 (1/8): Rust

📝 优化建议
   1. 将 Docker 经历扩展为「容器化 + K8s 编排」
   2. 在项目描述中增加分布式相关关键词
   3. 将「追求极致」的文化关键词自然融入自我评价
   4. 技能排序调整: Go → K8s → MySQL → Redis → ...

📈 评分对比
   优化前: 62/100 (关键词覆盖: 58%)
   优化后: 87/100 (关键词覆盖: 91%)
   提升: +25 分

✅ 优化后简历已生成: output/张三_字节跳动_后端开发_optimized.pdf
📊 完整报告已生成: output/张三_字节跳动_后端开发_report.md
```

---

## 七、实施路线

### Phase 1: MVP（4周）
> 目标：核心 pipeline 跑通，CLI 可用

- [ ] 项目骨架搭建（pyproject.toml, CLI, 配置）
- [ ] 简历解析（PDF + DOCX + MD）
- [ ] LLM 接口封装（LiteLLM + Ollama）
- [ ] JD 分析（关键词提取 + 分类）
- [ ] 简历优化（LLM 驱动，保持事实准确）
- [ ] ATS 评分（TF-IDF + LLM 语义打分）
- [ ] 多格式输出（PDF + DOCX + MD）
- [ ] 匹配报告生成
- [ ] 基础 Prompt 模板
- [ ] 单元测试

**Phase 1 交付物：**
```bash
cv-doctor optimize resume.pdf --jd "岗位描述..."
# 可用，但不包含公司分析
```

### Phase 2: 对症下药（3周）
> 目标：Target Mode 可用

- [ ] 天眼查 API 集成（公司工商信息）
- [ ] 公司官网爬取（About Us、技术博客）
- [ ] BOSS直聘 JD 采集（Playwright）
- [ ] 同公司多 JD 交叉分析
- [ ] 公司文化匹配分析
- [ ] 技术栈对齐分析
- [ ] 差距分析报告增强

**Phase 2 交付物：**
```bash
cv-doctor target resume.pdf --company "字节跳动" --position "后端开发"
# 完整的对症下药模式
```

### Phase 3: 增强 & Web（4周）
> 目标：用户体验完善，Web 前端

- [ ] 面试情报采集（牛客网面经）
- [ ] 面试引导点预埋
- [ ] 简历模板系统（HTML 模板 + WeasyPrint）
- [ ] Web 前端（Next.js）
- [ ] Docker 一键部署
- [ ] 多轮迭代优化（用户确认 → 再优化）
- [ ] 历史记录 & 对比

### Phase 4: 社区 & 生态（持续）
> 目标：开源社区建设

- [ ] 完善 README（中英双语）
- [ ] 贡献指南
- [ ] Issue 模板
- [ ] GitHub Actions CI
- [ ] PyPI 发布
- [ ] 推广（V2EX / 即刻 / Twitter / Reddit）

---

## 八、关键设计决策

### 8.1 事实准确性保障

简历优化最大的风险是 LLM 编造经历。对策：

1. **Prompt 约束**：明确要求 LLM 只优化表述，不添加新事实
2. **逐条确认**：每个修改都标注原始内容和修改内容
3. **Diff 输出**：像 git diff 一样展示所有变更
4. **用户审核**：优化结果以草稿形式呈现，用户可逐条接受/拒绝

### 8.2 隐私保护

1. **本地优先**：默认支持 Ollama，简历数据不出本机
2. **无服务器模式**：纯 CLI，不需要后端服务
3. **数据不持久化**：除非用户明确要求，否则不保存简历内容
4. **透明日志**：所有 LLM 调用的输入输出可查看

### 8.3 反爬策略

1. **BOSS直聘**：参考 boss-agent-cli 的方案（Playwright + 登录态）
2. **降级方案**：所有自动采集都支持手动粘贴替代
3. **限速**：采集间隔随机化，避免触发风控
4. **缓存**：同一公司信息本地缓存，避免重复采集

---

## 九、风险评估

| 风险 | 等级 | 对策 |
|------|------|------|
| BOSS直聘反爬升级 | 中 | 提供手动粘贴降级方案 |
| LLM 输出质量不稳定 | 中 | 多轮优化 + 用户确认 + Diff 展示 |
| PDF 解析准确度 | 中 | marker-pdf + 多引擎回退 |
| boss-agent-cli 功能扩展 | 低 | 专注深度优化，不做求职自动化 |
| 开源维护成本 | 低 | Phase 1 先跑通，不急于社区 |

---

## 十、竞品对比（最终版）

| 能力 | CV-Doctor | boss-agent-cli | JadeAI | resume-lm |
|------|-----------|----------------|--------|-----------|
| 简历解析 | ✅ PDF/DOCX/MD | ✅ | ✅ | ✅ |
| JD 关键词匹配 | ✅ | ❌ | ✅ | ✅ |
| ATS 评分 | ✅ 双引擎 | ❌ | ✅ | ❌ |
| 公司深度画像 | ✅⭐ | ❌ | ❌ | ❌ |
| 对症下药优化 | ✅⭐ | ❌ | ❌ | ❌ |
| 技术栈对齐 | ✅⭐ | ❌ | ❌ | ❌ |
| 面试引导预埋 | ✅⭐ | ❌ | ❌ | ❌ |
| BOSS直聘集成 | ✅ | ✅ | ❌ | ❌ |
| 本地 LLM | ✅ | ✅ | ❌ | ❌ |
| 中文优化 | ✅ | ✅ | ✅ | ❌ |
| 简历模板 | ✅ | ❌ | ✅✅ | ✅ |
| 求职自动化 | ❌（不做） | ✅✅ | ❌ | ❌ |

---

*最后更新: 2026-06-01*
*作者: 老大 + 露露緹婭*

"""CV-Doctor 核心数据模型 v2

基于可行性审查报告修订：
- 新增 Evidence Store 证据系统
- 新增 Policy Guard 安全策略
- 新增 Fact Ledger 事实账本
- Change 增加证据链
- Match Score 替代 ATS Score
- Surgery Report 替代简单 Match Report
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


# ==================== 枚举类型 ====================


class MatchLevel(str, Enum):
    """简历与 JD 要求的匹配程度"""

    FULL = "full"
    PARTIAL = "partial"
    MISSING = "missing"


class RequirementCategory(str, Enum):
    """JD 要求的分类"""

    HARD_SKILL = "hard_skill"
    SOFT_SKILL = "soft_skill"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    CERTIFICATION = "certification"
    OTHER = "other"


class FactSource(str, Enum):
    """事实来源"""

    RESUME = "resume"           # 来自用户简历
    USER_INPUT = "user_input"   # 来自用户手动输入
    JD = "jd"                   # 来自 JD 文本
    COMPANY = "company_source"  # 来自公司公开资料


class ChangeRisk(str, Enum):
    """修改风险等级"""

    LOW = "low"             # 改写表达、调整顺序
    MEDIUM = "medium"       # 数字化成果、技术深度提升
    HIGH = "high"           # 责任范围扩大、新技能加入


class ChangeStatus(str, Enum):
    """P0 审阅状态（API 用）"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class PolicyAction(str, Enum):
    """安全策略动作"""

    ALLOWED = "allowed"
    NEEDS_CONFIRMATION = "needs_confirmation"
    FORBIDDEN = "forbidden"


class OutputFormat(str, Enum):
    """输出格式"""

    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"


# ==================== 证据系统（v2 新增）====================


class Fact(BaseModel):
    """事实 — 证据库中的基本单元"""

    id: str
    text: str
    source: FactSource
    source_url: str = ""            # 来源链接（公司资料必填）
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    can_use_in_resume: bool = True
    requires_user_confirmation: bool = False


class EvidenceStore(BaseModel):
    """证据库 — 所有可用证据的集合"""

    facts: list[Fact] = Field(default_factory=list)

    def add(self, fact: Fact) -> None:
        """添加一条事实"""
        self.facts.append(fact)

    def get_by_source(self, source: FactSource) -> list[Fact]:
        """按来源筛选"""
        return [f for f in self.facts if f.source == source]

    def get_usable(self) -> list[Fact]:
        """获取可用于简历的事实"""
        return [f for f in self.facts if f.can_use_in_resume]

    def get_by_id(self, fact_id: str) -> Fact | None:
        """按 ID 获取"""
        for f in self.facts:
            if f.id == fact_id:
                return f
        return None


# ==================== 安全策略（v2 新增）====================


class PolicyGuard(BaseModel):
    """安全策略 — 控制哪些内容能写进简历"""

    # 硬规则：这些模式直接拒绝
    forbidden_patterns: list[str] = Field(
        default_factory=lambda: [
            "编造", "虚构", "不存在", "未参与", "未使用",
        ]
    )

    def check_change(self, change: Change) -> PolicyAction:
        """检查一条修改是否允许"""
        # 检查是否包含禁止模式
        for pattern in self.forbidden_patterns:
            if pattern in change.revised and pattern not in change.original:
                return PolicyAction.FORBIDDEN

        # 按风险等级判断
        if change.risk_level == ChangeRisk.LOW:
            return PolicyAction.ALLOWED
        elif change.risk_level == ChangeRisk.MEDIUM:
            return PolicyAction.NEEDS_CONFIRMATION
        else:  # HIGH
            return PolicyAction.NEEDS_CONFIRMATION


# ==================== 简历模型 ====================


class ContactInfo(BaseModel):
    """联系方式"""

    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    location: str = ""


class Experience(BaseModel):
    """工作经历"""

    company: str
    title: str
    duration: str = ""
    location: str = ""
    description: str = ""
    achievements: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class Education(BaseModel):
    """教育经历"""

    school: str
    degree: str = ""
    major: str = ""
    duration: str = ""
    gpa: str = ""
    highlights: list[str] = Field(default_factory=list)


class Project(BaseModel):
    """项目经历"""

    name: str
    role: str = ""
    duration: str = ""
    description: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class Resume(BaseModel):
    """简历完整模型"""

    name: str
    contact: ContactInfo = Field(default_factory=ContactInfo)
    summary: str = ""
    experiences: list[Experience] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    raw_text: str = ""


# ==================== JD 模型 ====================


class JobRequirement(BaseModel):
    """JD 中的一条要求"""

    text: str
    category: RequirementCategory
    is_mandatory: bool = True
    weight: float = Field(default=0.5, ge=0.0, le=1.0)
    match_level: MatchLevel = MatchLevel.MISSING
    resume_evidence: str = ""


class JobDescription(BaseModel):
    """岗位描述模型"""

    title: str
    company: str
    location: str = ""
    salary_range: str = ""
    description: str = ""
    requirements: list[JobRequirement] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)


# ==================== 公司画像模型 ====================


class CompanyClaim(BaseModel):
    """公司情报 — 每条带来源"""

    claim: str
    source_type: str        # tech_blog / official_site / github / news
    source_url: str = ""
    collected_at: str = ""
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class CompanyProfile(BaseModel):
    """公司画像"""

    name: str
    industry: str = ""
    size: str = ""
    funding_stage: str = ""
    founded: str = ""
    headquarters: str = ""
    website: str = ""
    description: str = ""
    culture_keywords: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    claims: list[CompanyClaim] = Field(default_factory=list)
    interview_insights: list[str] = Field(default_factory=list)


# ==================== Match Score（v2 改名）====================


class MatchScore(BaseModel):
    """投递匹配度（原 ATS Score）

    四维评分：
    - mandatory_coverage (40%): JD must-have 是否有简历证据
    - keyword_coverage (25%): 技能、工具、领域词覆盖
    - experience_relevance (25%): 项目/工作经历是否支持岗位要求
    - expression_quality (10%): 动词、量化、可读性
    """

    overall: float = Field(default=0.0, ge=0.0, le=100.0)
    mandatory_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    preferred_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    keyword_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    experience_relevance: float = Field(default=0.0, ge=0.0, le=100.0)
    expression_quality: float = Field(default=0.0, ge=0.0, le=100.0)


# ==================== 修改记录（v2 增强）====================


class Change(BaseModel):
    """单条修改记录 — v2 增加证据链"""

    id: str = ""                             # P0 API：稳定 id，供 PATCH
    section: str                            # e.g., "experiences[0].achievements[1]"
    original: str                           # 原文
    revised: str                            # 改后
    reason: str                             # 修改原因
    evidence_ids: list[str] = Field(default_factory=list)  # 引用的 Fact ID
    risk_level: ChangeRisk = ChangeRisk.LOW
    status: ChangeStatus = ChangeStatus.PENDING
    requires_user_confirmation: bool = False
    source_label: str = ""                  # "来自JD第3条" / "来自公司技术博客"


class ChangeSet(BaseModel):
    """修改集"""

    changes: list[Change] = Field(default_factory=list)

    @property
    def confirmed_changes(self) -> list[Change]:
        """直接应用的修改"""
        return [c for c in self.changes if not c.requires_user_confirmation]

    @property
    def pending_changes(self) -> list[Change]:
        """待用户确认的修改"""
        return [c for c in self.changes if c.requires_user_confirmation]

    @property
    def low_risk_count(self) -> int:
        return len([c for c in self.changes if c.risk_level == ChangeRisk.LOW])

    @property
    def medium_risk_count(self) -> int:
        return len([c for c in self.changes if c.risk_level == ChangeRisk.MEDIUM])

    @property
    def high_risk_count(self) -> int:
        return len([c for c in self.changes if c.risk_level == ChangeRisk.HIGH])


# ==================== 差距分析 & 手术报告 ====================


class GapReport(BaseModel):
    """差距分析报告"""

    match_score: MatchScore = Field(default_factory=MatchScore)
    requirements_analysis: list[JobRequirement] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)


class SurgeryReport(BaseModel):
    """手术报告 — 三件套之一"""

    match_score_before: MatchScore = Field(default_factory=MatchScore)
    match_score_after: MatchScore = Field(default_factory=MatchScore)
    gap_report: GapReport = Field(default_factory=GapReport)
    company_profile: CompanyProfile | None = None
    interview_highlights: list[str] = Field(default_factory=list)
    changes_summary: str = ""

    @property
    def score_improvement(self) -> float:
        """评分提升幅度"""
        return self.match_score_after.overall - self.match_score_before.overall


# ==================== 优化结果（v2 三件套）====================


class OptimizationResult(BaseModel):
    """优化结果 — v2 三件套"""

    original_resume: Resume
    optimized_resume: Resume
    changeset: ChangeSet                    # 修改 diff
    surgery_report: SurgeryReport           # 手术报告
    evidence_store: EvidenceStore = Field(default_factory=EvidenceStore)

    @property
    def score_improvement(self) -> float:
        return self.surgery_report.score_improvement

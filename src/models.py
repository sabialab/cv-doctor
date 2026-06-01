"""CV-Doctor 核心数据模型

所有模块共享的 Pydantic 模型定义。
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ==================== 枚举类型 ====================


class MatchLevel(str, Enum):
    """简历与 JD 要求的匹配程度"""

    FULL = "full"  # 完全匹配
    PARTIAL = "partial"  # 部分匹配
    MISSING = "missing"  # 缺失


class RequirementCategory(str, Enum):
    """JD 要求的分类"""

    HARD_SKILL = "hard_skill"  # 硬技能（编程语言、工具等）
    SOFT_SKILL = "soft_skill"  # 软技能（沟通、领导力等）
    EXPERIENCE = "experience"  # 经验要求（工作年限、行业经验）
    EDUCATION = "education"  # 学历要求
    CERTIFICATION = "certification"  # 证书要求
    OTHER = "other"


class OutputFormat(str, Enum):
    """输出格式"""

    PDF = "pdf"
    DOCX = "docx"
    MARKDOWN = "markdown"


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
    duration: str = ""  # e.g., "2022.03 - 2024.06"
    location: str = ""
    description: str = ""
    achievements: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)


class Education(BaseModel):
    """教育经历"""

    school: str
    degree: str = ""  # e.g., "本科", "硕士"
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
    raw_text: str = ""  # 原始文本（用于回退）


# ==================== JD 模型 ====================


class JobRequirement(BaseModel):
    """JD 中的一条要求"""

    text: str
    category: RequirementCategory
    is_mandatory: bool = True  # True=必须项, False=加分项
    weight: float = Field(default=0.5, ge=0.0, le=1.0)  # 重要程度
    match_level: MatchLevel = MatchLevel.MISSING
    resume_evidence: str = ""  # 简历中的对应证据（如有）


class JobDescription(BaseModel):
    """岗位描述模型"""

    title: str
    company: str
    location: str = ""
    salary_range: str = ""
    description: str = ""  # JD 原始文本
    requirements: list[JobRequirement] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)  # 提取的关键词
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)


# ==================== 公司画像模型 ====================


class CompanyProfile(BaseModel):
    """公司画像"""

    name: str
    industry: str = ""
    size: str = ""  # e.g., "10000-100000人"
    funding_stage: str = ""  # e.g., "已上市", "C轮"
    founded: str = ""
    headquarters: str = ""
    website: str = ""
    description: str = ""

    # 深度分析字段
    culture_keywords: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)
    tech_blog_url: str = ""
    github_org: str = ""

    # 面试相关
    interview_insights: list[str] = Field(default_factory=list)
    interview_difficulty: str = ""  # e.g., "中等", "困难"

    # 数据来源
    data_sources: list[str] = Field(default_factory=list)


# ==================== 分析报告模型 ====================


class RequirementAnalysis(BaseModel):
    """单条要求的分析结果"""

    requirement: JobRequirement
    match_level: MatchLevel
    resume_evidence: str = ""  # 简历中的对应内容
    optimization_suggestion: str = ""  # 优化建议


class MatchReport(BaseModel):
    """匹配度报告"""

    overall_score: float = Field(default=0.0, ge=0.0, le=100.0)
    keyword_coverage: float = Field(default=0.0, ge=0.0, le=100.0)
    culture_fit: float = Field(default=0.0, ge=0.0, le=100.0)
    tech_stack_match: float = Field(default=0.0, ge=0.0, le=100.0)

    # 逐条分析
    requirements_analysis: list[RequirementAnalysis] = Field(default_factory=list)

    # 汇总
    strengths: list[str] = Field(default_factory=list)  # 优势项
    gaps: list[str] = Field(default_factory=list)  # 差距项
    suggestions: list[str] = Field(default_factory=list)  # 优化建议


class ChangeRecord(BaseModel):
    """简历修改记录"""

    section: str  # e.g., "experiences[0].achievements[1]"
    original: str
    optimized: str
    reason: str  # 修改原因


class OptimizationResult(BaseModel):
    """优化结果"""

    original_resume: Resume
    optimized_resume: Resume
    original_score: MatchReport
    optimized_score: MatchReport
    changes: list[ChangeRecord] = Field(default_factory=list)
    company_profile: CompanyProfile | None = None  # Target Mode 独有
    job_description: JobDescription | None = None

    @property
    def score_improvement(self) -> float:
        """评分提升幅度"""
        return self.optimized_score.overall_score - self.original_score.overall_score

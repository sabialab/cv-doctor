"""基础测试 — 验证项目结构和数据模型"""

from pathlib import Path

import pytest

from src.models import (
    Resume,
    ContactInfo,
    Experience,
    Education,
    Project,
    JobDescription,
    JobRequirement,
    CompanyProfile,
    MatchReport,
    OptimizationResult,
    MatchLevel,
    RequirementCategory,
)


class TestModels:
    """数据模型测试"""

    def test_resume_creation(self):
        """测试简历模型创建"""
        resume = Resume(
            name="张三",
            contact=ContactInfo(email="zhangsan@example.com", phone="13800138000"),
            summary="5年后端开发经验",
            experiences=[
                Experience(
                    company="字节跳动",
                    title="后端开发工程师",
                    duration="2022.03 - 2024.06",
                    achievements=["优化接口响应时间降低 40%"],
                    keywords=["Go", "微服务", "K8s"],
                )
            ],
            education=[
                Education(school="北京大学", degree="本科", major="计算机科学")
            ],
            skills=["Go", "Python", "MySQL", "Redis", "Docker"],
        )

        assert resume.name == "张三"
        assert len(resume.experiences) == 1
        assert resume.experiences[0].company == "字节跳动"
        assert "Go" in resume.skills

    def test_job_description_creation(self):
        """测试 JD 模型创建"""
        jd = JobDescription(
            title="后端开发工程师",
            company="字节跳动",
            location="北京",
            requirements=[
                JobRequirement(
                    text="熟悉 Go 语言",
                    category=RequirementCategory.HARD_SKILL,
                    is_mandatory=True,
                    weight=0.9,
                ),
                JobRequirement(
                    text="良好的沟通能力",
                    category=RequirementCategory.SOFT_SKILL,
                    is_mandatory=False,
                    weight=0.5,
                ),
            ],
            keywords=["Go", "微服务", "分布式"],
        )

        assert jd.title == "后端开发工程师"
        assert len(jd.requirements) == 2
        assert jd.requirements[0].is_mandatory is True

    def test_company_profile_creation(self):
        """测试公司画像模型创建"""
        profile = CompanyProfile(
            name="字节跳动",
            industry="互联网",
            size="100000+人",
            funding_stage="已上市",
            culture_keywords=["追求极致", "开放谦逊"],
            tech_stack=["Go", "Rust", "K8s"],
        )

        assert profile.name == "字节跳动"
        assert "追求极致" in profile.culture_keywords

    def test_match_report_score_range(self):
        """测试匹配报告分数范围"""
        report = MatchReport(
            overall_score=85.5,
            keyword_coverage=90.0,
            culture_fit=80.0,
            tech_stack_match=85.0,
        )

        assert 0 <= report.overall_score <= 100
        assert 0 <= report.keyword_coverage <= 100

    def test_optimization_result_score_improvement(self):
        """测试优化结果的评分提升计算"""
        result = OptimizationResult(
            original_resume=Resume(name="张三"),
            optimized_resume=Resume(name="张三"),
            original_score=MatchReport(overall_score=60.0),
            optimized_score=MatchReport(overall_score=85.0),
        )

        assert result.score_improvement == 25.0

    def test_match_level_enum(self):
        """测试匹配等级枚举"""
        assert MatchLevel.FULL == "full"
        assert MatchLevel.PARTIAL == "partial"
        assert MatchLevel.MISSING == "missing"


class TestConfig:
    """配置测试"""

    def test_config_loads(self):
        """测试配置能正常加载"""
        from src.config import config

        assert config.llm.provider in [
            "openai", "anthropic", "ollama", "gemini",
        ] or config.llm.provider  # 允许任何非空值
        assert config.llm.model  # 模型名非空


class TestCLI:
    """CLI 测试"""

    def test_cli_imports(self):
        """测试 CLI 模块能正常导入"""
        from src.cli import app

        assert app is not None

    def test_version(self):
        """测试版本号"""
        from src import __version__

        assert __version__ == "0.1.0"

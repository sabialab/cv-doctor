"""基础测试 — 验证项目结构和数据模型 v2"""

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
    CompanyClaim,
    MatchScore,
    GapReport,
    SurgeryReport,
    OptimizationResult,
    MatchLevel,
    RequirementCategory,
    Fact,
    FactSource,
    EvidenceStore,
    Change,
    ChangeSet,
    ChangeRisk,
    PolicyGuard,
    PolicyAction,
)


# ==================== 证据系统测试 ====================


class TestEvidenceStore:
    """证据库测试"""

    def test_add_and_get_facts(self):
        store = EvidenceStore()
        store.add(Fact(id="f1", text="熟悉 Go 语言", source=FactSource.RESUME))
        store.add(Fact(id="f2", text="要求 Go 经验", source=FactSource.JD))
        store.add(Fact(id="f3", text="技术栈以 Go 为主", source=FactSource.COMPANY))

        assert len(store.facts) == 3
        assert len(store.get_by_source(FactSource.RESUME)) == 1
        assert len(store.get_by_source(FactSource.JD)) == 1

    def test_get_usable_facts(self):
        store = EvidenceStore()
        store.add(Fact(id="f1", text="Go 开发", source=FactSource.RESUME, can_use_in_resume=True))
        store.add(Fact(id="f2", text="未验证", source=FactSource.COMPANY, can_use_in_resume=False))

        usable = store.get_usable()
        assert len(usable) == 1
        assert usable[0].id == "f1"

    def test_get_by_id(self):
        store = EvidenceStore()
        store.add(Fact(id="f1", text="Go", source=FactSource.RESUME))

        assert store.get_by_id("f1") is not None
        assert store.get_by_id("f999") is None


class TestPolicyGuard:
    """安全策略测试"""

    def test_low_risk_allowed(self):
        guard = PolicyGuard()
        change = Change(
            section="summary",
            original="熟悉 Go",
            revised="熟练掌握 Go 语言开发",
            reason="强化表述",
            risk_level=ChangeRisk.LOW,
        )
        assert guard.check_change(change) == PolicyAction.ALLOWED

    def test_medium_risk_needs_confirmation(self):
        guard = PolicyGuard()
        change = Change(
            section="experiences[0].achievements[0]",
            original="参与项目开发",
            revised="主导核心模块开发，性能提升 40%",
            reason="量化成果",
            risk_level=ChangeRisk.MEDIUM,
        )
        assert guard.check_change(change) == PolicyAction.NEEDS_CONFIRMATION

    def test_forbidden_pattern_blocked(self):
        guard = PolicyGuard()
        change = Change(
            section="skills",
            original="Go",
            revised="Go, K8s 生产集群管理经验（编造）",
            reason="添加技能",
            risk_level=ChangeRisk.HIGH,
        )
        assert guard.check_change(change) == PolicyAction.FORBIDDEN


class TestChangeSet:
    """修改集测试"""

    def test_confirmed_and_pending(self):
        changeset = ChangeSet(changes=[
            Change(section="s1", original="a", revised="b", reason="r",
                   risk_level=ChangeRisk.LOW),
            Change(section="s2", original="c", revised="d", reason="r",
                   risk_level=ChangeRisk.MEDIUM, requires_user_confirmation=True),
        ])
        assert len(changeset.confirmed_changes) == 1
        assert len(changeset.pending_changes) == 1

    def test_risk_counts(self):
        changeset = ChangeSet(changes=[
            Change(section="s1", original="a", revised="b", reason="r",
                   risk_level=ChangeRisk.LOW),
            Change(section="s2", original="c", revised="d", reason="r",
                   risk_level=ChangeRisk.LOW),
            Change(section="s3", original="e", revised="f", reason="r",
                   risk_level=ChangeRisk.MEDIUM),
            Change(section="s4", original="g", revised="h", reason="r",
                   risk_level=ChangeRisk.HIGH),
        ])
        assert changeset.low_risk_count == 2
        assert changeset.medium_risk_count == 1
        assert changeset.high_risk_count == 1


# ==================== Match Score 测试 ====================


class TestMatchScore:
    """Match Score 测试"""

    def test_score_range(self):
        score = MatchScore(
            overall=85.0,
            mandatory_coverage=90.0,
            keyword_coverage=80.0,
            experience_relevance=85.0,
            expression_quality=75.0,
        )
        assert 0 <= score.overall <= 100

    def test_default_zero(self):
        score = MatchScore()
        assert score.overall == 0.0


# ==================== 手术报告测试 ====================


class TestSurgeryReport:
    """手术报告测试"""

    def test_score_improvement(self):
        report = SurgeryReport(
            match_score_before=MatchScore(overall=60.0),
            match_score_after=MatchScore(overall=85.0),
        )
        assert report.score_improvement == 25.0


# ==================== 简历模型测试 ====================


class TestResume:
    """简历模型测试"""

    def test_resume_creation(self):
        resume = Resume(
            name="张三",
            contact=ContactInfo(email="zhangsan@example.com"),
            summary="5年后端开发经验",
            experiences=[
                Experience(
                    company="字节跳动",
                    title="后端开发工程师",
                    achievements=["优化接口响应时间降低 40%"],
                )
            ],
            education=[Education(school="北京大学", degree="本科", major="计算机科学")],
            skills=["Go", "Python", "MySQL"],
        )
        assert resume.name == "张三"
        assert len(resume.experiences) == 1
        assert "Go" in resume.skills

    def test_job_description_creation(self):
        jd = JobDescription(
            title="后端开发工程师",
            company="字节跳动",
            requirements=[
                JobRequirement(
                    text="熟悉 Go 语言",
                    category=RequirementCategory.HARD_SKILL,
                    is_mandatory=True,
                    weight=0.9,
                ),
            ],
        )
        assert jd.requirements[0].is_mandatory is True

    def test_company_profile_with_claims(self):
        profile = CompanyProfile(
            name="字节跳动",
            culture_keywords=["追求极致"],
            claims=[
                CompanyClaim(
                    claim="技术栈以 Go 为主",
                    source_type="tech_blog",
                    source_url="https://tech.bytedance.com/...",
                    confidence=0.85,
                )
            ],
        )
        assert len(profile.claims) == 1
        assert profile.claims[0].confidence == 0.85


# ==================== 优化结果测试 ====================


class TestOptimizationResult:
    """优化结果测试"""

    def test_full_optimization_result(self):
        result = OptimizationResult(
            original_resume=Resume(name="张三"),
            optimized_resume=Resume(name="张三"),
            changeset=ChangeSet(changes=[
                Change(
                    section="summary",
                    original="熟悉 Go",
                    revised="熟练掌握 Go 语言",
                    reason="强化表述",
                    evidence_ids=["f1"],
                    risk_level=ChangeRisk.LOW,
                )
            ]),
            surgery_report=SurgeryReport(
                match_score_before=MatchScore(overall=60.0),
                match_score_after=MatchScore(overall=85.0),
            ),
        )
        assert result.score_improvement == 25.0
        assert len(result.changeset.changes) == 1
        assert result.changeset.changes[0].evidence_ids == ["f1"]


# ==================== 配置测试 ====================


class TestConfig:
    """配置测试"""

    def test_config_loads(self):
        from src.config import config
        assert config.llm.provider
        assert config.llm.model


# ==================== CLI 测试 ====================


class TestCLI:
    """CLI 测试"""

    def test_cli_imports(self):
        from src.cli import app
        assert app is not None

    def test_version(self):
        from src import __version__
        assert __version__ == "0.1.0"

"""P0 桩流水线：不调用 LLM，返回固定 DiagnosisResult 便于前后端联调。"""

from __future__ import annotations

import uuid

from src.models import Change, ChangeRisk, ChangeStatus
from src.p0_models import (
    DiagnosisResult,
    GapItem,
    GapSeverity,
    GapType,
    JDInterpretation,
    MatchStatus,
    P0GapReport,
    P0MatchScore,
    PolicyGuardSummary,
)


def build_stub_diagnosis() -> DiagnosisResult:
    """与 docs/p0-mvp-implementation.md §4.2 示例结构一致。"""
    return DiagnosisResult(
        jd_interpretation=JDInterpretation(
            role_summary="高级后端工程师，负责 API 与数据管道。",
            hard_requirements=["Python 3 年以上", "熟悉 FastAPI 或同类框架"],
            preferred_requirements=["有云服务或容器经验"],
            keywords=["Python", "FastAPI", "PostgreSQL"],
            responsibilities=["设计与维护 REST API", "参与数据管道建设"],
            nice_to_have=["Kubernetes 经验"],
        ),
        match_score=P0MatchScore(
            overall=72,
            hard_requirement_score=80,
            preferred_score=65,
            keyword_coverage=70,
            responsibility_alignment=68,
            status=MatchStatus.PARTIAL,
            breakdown={
                "hard_requirement_score": 80,
                "preferred_score": 65,
                "keyword_coverage": 70,
                "responsibility_alignment": 68,
            },
        ),
        gap_report=P0GapReport(
            matched=["熟悉 FastAPI 相关技术栈"],
            partial_match=[
                GapItem(
                    requirement="Python 3 年以上",
                    severity=GapSeverity.MEDIUM,
                    suggestion="可补充项目年限表述，勿夸大",
                    gap_type=GapType.EXPERIENCE,
                )
            ],
            hard_missing=[
                GapItem(
                    requirement="Python 3 年以上",
                    severity=GapSeverity.HIGH,
                    suggestion="在工作经历中补充 Python 项目年限与规模",
                    gap_type=GapType.EXPERIENCE,
                )
            ],
            preferred_missing=[
                GapItem(
                    requirement="云服务经验",
                    severity=GapSeverity.MEDIUM,
                    suggestion="补充 AWS/Cloudflare 相关项目描述",
                    gap_type=GapType.EXPERIENCE,
                )
            ],
            keyword_missing=["FastAPI"],
            responsibility_gaps=["数据管道"],
            overreach_risks=[],
            total_gaps=3,
        ),
        changes=[
            Change(
                id=str(uuid.uuid4()),
                section="summary",
                original="负责后端开发与维护。",
                revised="负责后端 API 设计与开发，使用 FastAPI 构建高可用服务。",
                reason="JD 强调 API 设计与 FastAPI；简历表述过泛。",
                evidence_ids=["stub-evidence-summary"],
                risk_level=ChangeRisk.LOW,
                status=ChangeStatus.PENDING,
                requires_user_confirmation=False,
                source_label="来自 JD 职责描述",
            ),
            Change(
                id=str(uuid.uuid4()),
                section="skills",
                original="熟悉 Python",
                revised="Python（3+ 年），FastAPI，PostgreSQL",
                reason="补齐 JD 关键词与硬性要求。",
                evidence_ids=["stub-evidence-skills"],
                risk_level=ChangeRisk.LOW,
                status=ChangeStatus.PENDING,
                requires_user_confirmation=False,
                source_label="来自 JD 关键词",
            ),
            Change(
                id=str(uuid.uuid4()),
                section="experiences[0].achievements[0]",
                original="参与内部系统开发",
                revised="设计并实现 REST API，支撑日均 10 万请求",
                reason="数字化成果，对齐 JD 数据管道职责。",
                evidence_ids=["stub-evidence-experience"],
                risk_level=ChangeRisk.MEDIUM,
                status=ChangeStatus.PENDING,
                requires_user_confirmation=True,
                source_label="来自 JD 职责描述",
            ),
        ],
        policy_guard=PolicyGuardSummary(
            passed=True,
            blocked_count=0,
            downgraded_count=0,
            blocked_items=[],
            warnings=[],
        ),
        processing_time_ms=1200,
        model_used="stub-p0",
    )

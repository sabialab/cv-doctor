"""Policy guard service tests."""

from __future__ import annotations

from src.models import Change, ChangeRisk
from src.services.policy_guard import apply_policy_guard


def test_blocks_changes_without_evidence():
    changes = [
        Change(
            id="1",
            section="summary",
            original="旧",
            revised="新",
            reason="test",
            evidence_ids=[],
            risk_level=ChangeRisk.LOW,
        )
    ]
    passed, summary = apply_policy_guard(changes)
    assert passed == []
    assert summary.blocked_count == 1


def test_allows_low_risk_with_evidence():
    changes = [
        Change(
            id="1",
            section="summary",
            original="熟悉 Python",
            revised="Python（3 年）",
            reason="对齐 JD",
            evidence_ids=["fact-skill-python-0"],
            risk_level=ChangeRisk.LOW,
        )
    ]
    passed, summary = apply_policy_guard(changes)
    assert len(passed) == 1
    assert summary.passed is True

"""Policy Guard service — filter changes before API response."""

from __future__ import annotations

from src.models import Change, PolicyAction, PolicyGuard
from src.p0_models import PolicyGuardSummary


def apply_policy_guard(changes: list[Change]) -> tuple[list[Change], PolicyGuardSummary]:
    """Filter forbidden / no-evidence changes; mark confirmation requirements."""
    guard = PolicyGuard()
    passed: list[Change] = []
    blocked_items: list[str] = []
    warnings: list[str] = []
    downgraded = 0

    for change in changes:
        if not change.evidence_ids:
            blocked_items.append(change.section or change.original[:30])
            continue

        action = guard.check_change(change)
        if action == PolicyAction.FORBIDDEN:
            blocked_items.append(change.section or "forbidden")
            continue

        if action == PolicyAction.NEEDS_CONFIRMATION:
            change.requires_user_confirmation = True
            downgraded += 1
            if change.risk_level.value == "high":
                warnings.append(f"高风险修改需确认：{change.section}")

        passed.append(change)

    summary = PolicyGuardSummary(
        passed=len(blocked_items) == 0,
        blocked_count=len(blocked_items),
        downgraded_count=downgraded,
        blocked_items=blocked_items,
        warnings=warnings,
    )
    return passed, summary

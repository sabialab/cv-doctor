"""Export trust boundary — which accepted changes may be written to export files."""

from __future__ import annotations

from src.models import Change, ChangeRisk, ChangeStatus


def exportable_changes(changes: list[Change]) -> list[Change]:
    """Accepted changes safe to merge into export (HIGH risk never exported)."""
    return [
        c
        for c in changes
        if c.status == ChangeStatus.ACCEPTED and c.risk_level != ChangeRisk.HIGH
    ]

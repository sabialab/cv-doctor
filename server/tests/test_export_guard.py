"""Export trust boundary tests."""

from __future__ import annotations

import uuid

from src.models import Change, ChangeRisk, ChangeStatus
from src.services.export_guard import exportable_changes


def test_high_risk_accepted_not_exportable():
    changes = [
        Change(
            id=str(uuid.uuid4()),
            section="exp",
            original="a",
            revised="b",
            reason="r",
            evidence_ids=["f1"],
            risk_level=ChangeRisk.HIGH,
            status=ChangeStatus.ACCEPTED,
        ),
        Change(
            id=str(uuid.uuid4()),
            section="skills",
            original="c",
            revised="d",
            reason="r",
            evidence_ids=["f2"],
            risk_level=ChangeRisk.LOW,
            status=ChangeStatus.ACCEPTED,
        ),
    ]
    exportable = exportable_changes(changes)
    assert len(exportable) == 1
    assert exportable[0].risk_level == ChangeRisk.LOW


def test_pending_not_exportable():
    changes = [
        Change(
            id="1",
            section="s",
            original="a",
            revised="b",
            reason="r",
            evidence_ids=["f1"],
            risk_level=ChangeRisk.LOW,
            status=ChangeStatus.PENDING,
        ),
    ]
    assert exportable_changes(changes) == []

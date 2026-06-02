"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from src.services.rate_limit import reset_for_tests


@pytest.fixture(autouse=True)
def _rate_limit_test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Most API tests create many sessions; keep rate limit off unless a test opts in."""
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "0")
    reset_for_tests()

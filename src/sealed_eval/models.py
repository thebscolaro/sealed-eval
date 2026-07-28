from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class CheckMode(str, Enum):
    holdout_golden = "holdout_golden"
    differential = "differential"
    contract = "contract"
    invariant = "invariant"


class TaskCard(BaseModel):
    id: str
    title: str
    summary: str
    public_acceptance: list[str] = Field(default_factory=list)


class Case(BaseModel):
    id: str
    check: CheckMode
    bucket: str = "general"
    request: dict[str, Any] = Field(default_factory=dict)
    expect: dict[str, Any] = Field(default_factory=dict)
    visible: bool = False  # hold-out by default


class SuiteStatus(str, Enum):
    draft = "draft"
    sealed = "sealed"


class Scorecard(BaseModel):
    suite_id: str
    passed: bool
    total: int
    ok: int
    visible_ok: int = 0
    heldout_ok: int = 0
    visible_heldout_gap: float = 0.0
    buckets: dict[str, dict[str, int]] = Field(default_factory=dict)
    gate: str = "fail"  # pass | fail | retry

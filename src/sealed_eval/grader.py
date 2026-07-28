from __future__ import annotations

from sealed_eval.checks import run_case
from sealed_eval.models import Scorecard
from sealed_eval.store import SealedStore


def apply_gate(
    score: Scorecard,
    *,
    pass_threshold: float = 1.0,
    max_gap: float = 0.25,
) -> Scorecard:
    rate = (score.ok / score.total) if score.total else 0.0
    if rate >= pass_threshold and score.visible_heldout_gap <= max_gap:
        score.gate = "pass"
        score.passed = True
    elif rate >= pass_threshold * 0.8:
        score.gate = "retry"
        score.passed = False
    else:
        score.gate = "fail"
        score.passed = False
    return score


def grade_artifact(
    store: SealedStore,
    suite_id: str,
    artifact_base_url: str,
    seal_token: str,
    *,
    pass_threshold: float = 1.0,
    max_gap: float = 0.25,
) -> Scorecard:
    store.require_seal(suite_id, seal_token)
    cases = store.load_cases(suite_id)
    ctx: dict = {}
    buckets: dict[str, dict[str, int]] = {}
    ok = 0
    visible_ok = 0
    heldout_ok = 0
    visible_n = 0
    heldout_n = 0

    for case in cases:
        buckets.setdefault(case.bucket, {"ok": 0, "fail": 0})
        passed, _reason = run_case(case, artifact_base_url, ctx)
        if passed:
            ok += 1
            buckets[case.bucket]["ok"] += 1
            if case.visible:
                visible_ok += 1
            else:
                heldout_ok += 1
        else:
            buckets[case.bucket]["fail"] += 1
        if case.visible:
            visible_n += 1
        else:
            heldout_n += 1

    total = len(cases)
    v_rate = (visible_ok / visible_n) if visible_n else 1.0
    h_rate = (heldout_ok / heldout_n) if heldout_n else 1.0
    gap = max(0.0, v_rate - h_rate)
    score = Scorecard(
        suite_id=suite_id,
        passed=False,
        total=total,
        ok=ok,
        visible_ok=visible_ok,
        heldout_ok=heldout_ok,
        visible_heldout_gap=gap,
        buckets=buckets,
        gate="fail",
    )
    score = apply_gate(score, pass_threshold=pass_threshold, max_gap=max_gap)
    store.save_scorecard(suite_id, score)
    return score

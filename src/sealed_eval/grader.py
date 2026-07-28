from __future__ import annotations

from sealed_eval.checks import run_contract
from sealed_eval.models import CheckMode, Scorecard
from sealed_eval.store import SealedStore


def grade_artifact(
    store: SealedStore,
    suite_id: str,
    artifact_base_url: str,
    seal_token: str,
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
        if case.check == CheckMode.contract:
            passed, _reason = run_contract(case, artifact_base_url, ctx)
        else:
            # ponytail: other modes stub-fail until adapters land
            passed, _reason = False, "unsupported_check"

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
    passed = ok == total and total > 0
    return Scorecard(
        suite_id=suite_id,
        passed=passed,
        total=total,
        ok=ok,
        visible_ok=visible_ok,
        heldout_ok=heldout_ok,
        visible_heldout_gap=gap,
        buckets=buckets,
        gate="pass" if passed else "fail",
    )

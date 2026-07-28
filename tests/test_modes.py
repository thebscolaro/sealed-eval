"""Tests for multi-mode checks and markdown propose."""

from sealed_eval.checks import run_case, run_invariant, run_json_probe
from sealed_eval.models import Case, CheckMode
from sealed_eval.propose import propose_from_markdown


def test_propose_markdown_modes():
    body = """Accept:
- GET /health returns 200
- response never contains traceback
- UI page shows Orders
- health golden matches ok
"""
    card, cases = propose_from_markdown("t1", "T", body)
    assert card.id == "t1"
    modes = {c.check for c in cases}
    assert CheckMode.contract in modes
    assert CheckMode.invariant in modes
    assert CheckMode.ui in modes
    assert CheckMode.holdout_golden in modes


def test_invariant_never_contains(tmp_path=None):
    case = Case(
        id="i",
        check=CheckMode.invariant,
        request={},
        expect={"never_contains": ["boom"]},
    )
    ok, _ = run_invariant(case, "http://x", {"last_body": {"ok": True}, "last_text": '{"ok":true}'})
    assert ok
    bad, reason = run_invariant(case, "http://x", {"last_body": {}, "last_text": "boom"})
    assert not bad and "never_contains" in reason


def test_json_probe_echo():
    case = Case(
        id="p",
        check=CheckMode.json_probe,
        request={"argv": ["python3", "-c", "print('{\"a\":1}')"]},
        expect={"exit_code": 0, "jsonpath_equals": {"a": 1}},
    )
    ok, reason = run_json_probe(case, "http://unused", {})
    assert ok, reason


def test_run_case_unsupported():
    case = Case(id="x", check=CheckMode.differential, request={}, expect={})
    ok, reason = run_case(case, "http://x", {})
    assert not ok and reason == "unsupported_check"

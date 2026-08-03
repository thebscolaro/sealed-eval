"""Tests for multi-mode checks and markdown propose."""

import pytest

from sealed_eval.checks import run_case, run_invariant, run_json_probe
from sealed_eval.models import Case, CheckMode
from sealed_eval.propose import propose_from_markdown
from sealed_eval.survey import survey_subject


def test_propose_requires_quoted_ui():
    body = """Accept:
- GET /health returns 200
- UI page shows Get started without quotes
"""
    with pytest.raises(ValueError, match="no draft cases|quoted"):
        # health alone may still produce a case — use only unquoted UI
        propose_from_markdown(
            "t0",
            "T",
            'Accept:\n- Landing page shows Get started\n',
        )


def test_propose_quoted_ui_and_http():
    body = """Accept:
- GET /health returns 200
- UI page shows "Hello"
- health golden matches ok
"""
    card, cases = propose_from_markdown("t1", "T", body)
    assert card.id == "t1"
    modes = {c.check for c in cases}
    assert CheckMode.contract in modes
    assert CheckMode.ui in modes
    assert CheckMode.holdout_golden in modes
    ui = next(c for c in cases if c.check == CheckMode.ui)
    assert ui.expect.get("text") == "Hello"


def test_propose_approved_section():
    body = """## From repository
- junk _(source: x)_

## Accept (approved)

Accept:
- Page shows "Welcome"
"""
    _, cases = propose_from_markdown("t2", "T", body)
    assert len(cases) == 1
    assert cases[0].expect.get("text") == "Welcome"


def test_survey_subject_smoke(tmp_path):
    (tmp_path / "README.md").write_text(
        "# App\n\n- Fancy feature bullet\n\n## Acceptance\n- Page shows \"Hi\"\n",
        encoding="utf-8",
    )
    (tmp_path / "package.json").write_text('{"scripts":{"build":"vite build","dev":"vite"}}', encoding="utf-8")
    text = survey_subject(tmp_path)
    assert "Survey candidates" in text
    assert "Novel acceptance" in text
    assert "Low-confidence heuristics" in text
    assert "Hi" in text or "shows" in text.lower()
    assert "Fancy feature bullet" not in text
    assert 'npm script "build"' in text
    assert 'npm script "dev"' not in text


def test_survey_skips_dep_bump_titles():
    from sealed_eval.survey import _is_gh_noise

    assert _is_gh_noise("chore(deps-dev): bump vite from 5 to 6")
    assert _is_gh_noise("Bump eslint from 8 to 9")
    assert not _is_gh_noise("Add PIN login acceptance")


def test_suite_id_rejects_traversal(tmp_path):
    from sealed_eval.store import SealedStore

    store = SealedStore(tmp_path)
    try:
        store._suite_dir("../escape")
        raise AssertionError("expected ValueError")
    except ValueError:
        pass


def test_invariant_requires_path():
    case = Case(
        id="i",
        check=CheckMode.invariant,
        request={},
        expect={"never_contains": ["boom"]},
    )
    ok, reason = run_invariant(case, "http://x", {})
    assert not ok and reason == "no_path"


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

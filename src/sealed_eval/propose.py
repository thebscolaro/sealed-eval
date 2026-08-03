from __future__ import annotations

import re
import sys
from pathlib import Path

from sealed_eval.capabilities import import_cases_json
from sealed_eval.models import Case, CheckMode, TaskCard

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
_HTTP = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)", re.I)
_QUOTED = re.compile(r'["“]([^"”]+)["”]|\'([^\']+)\'')
_EXPLICIT_TEXT = re.compile(r"(?i)\btext:\s*(\S.+)$")
_EXPLICIT_SEL = re.compile(r"(?i)\bselector:\s*(\S.+)$")


def _ui_expect(bullet: str) -> dict | None:
    """Require quoted string or text:/selector: — no CapWord/App guesses."""
    m = _EXPLICIT_TEXT.search(bullet)
    if m:
        return {"text": m.group(1).strip().strip(",.")}
    m = _EXPLICIT_SEL.search(bullet)
    if m:
        return {"selector": m.group(1).strip().strip(",.")}
    m = _QUOTED.search(bullet)
    if m:
        return {"text": next(g for g in m.groups() if g)}
    return None


def _extract_ac(body: str) -> list[str]:
    """Prefer ## Accept (approved); else Accept: section; else all bullets."""
    lines = body.splitlines()
    approved: list[str] = []
    take = False
    for ln in lines:
        if ln.strip().lower().startswith("## accept (approved)"):
            take = True
            continue
        if take and ln.strip().startswith("##"):
            break
        if take:
            s = ln.strip()
            if s.lower().startswith("accept"):
                rest = s.split(":", 1)[-1].strip() if ":" in s else ""
                if rest:
                    approved.append(rest)
                continue
            if s.startswith("-"):
                item = s.lstrip("- ").strip()
                if item and item != "-" and not item.startswith("_("):
                    approved.append(re.sub(r"\s*_\(source:[^)]+\)_\s*$", "", item).strip())
    if any(x for x in approved if len(x) > 2):
        return [x for x in approved if len(x) > 2][:20]

    ac: list[str] = []
    in_accept = False
    for ln in lines:
        s = ln.strip()
        low = s.lower()
        if low.startswith("accept"):
            in_accept = True
            rest = s.split(":", 1)[-1].strip() if ":" in s else ""
            if rest:
                ac.append(rest)
            continue
        if in_accept:
            if s.startswith("##"):
                break
            if s.startswith("-"):
                item = s.lstrip("- ").strip()
                if item:
                    ac.append(re.sub(r"\s*_\(source:[^)]+\)_\s*$", "", item).strip())
    if ac:
        return ac[:20]

    # fallback: any markdown bullets
    for ln in lines:
        s = ln.strip()
        if s.startswith("-"):
            item = s.lstrip("- ").strip()
            if item and not item.startswith("_(") and "source:" not in item.lower():
                ac.append(item)
    return ac[:20]


def propose_from_markdown(suite_id: str, title: str, body: str) -> tuple[TaskCard, list[Case]]:
    """Draft cases from AC bullets; operator must review then seal."""
    ac = _extract_ac(body)
    card = TaskCard(
        id=suite_id,
        title=title,
        summary=body.strip().splitlines()[0][:200] if body.strip() else title,
        public_acceptance=ac[:20] or ["behavior matches sealed corpus"],
    )
    cases: list[Case] = []
    skipped: list[str] = []

    for i, bullet in enumerate(ac[:20]):
        low = bullet.lower()
        cid = f"ac-{i + 1}"
        m = _HTTP.search(bullet)
        if m:
            method, path = m.group(1).upper(), m.group(2).rstrip(".,)")
            status = 201 if method == "POST" else 200
            req: dict = {"method": method, "path": path}
            if method == "POST" and path.rstrip("/").endswith("orders"):
                req["json"] = {"sku": "demo", "qty": 1}
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.contract,
                    bucket="http",
                    request=req,
                    expect={"status": status},
                    visible=("health" in path) or (not cases),
                )
            )
            continue
        if any(k in low for k in ("golden", "matches fixture", "exact body")) and "health" in low:
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.holdout_golden,
                    bucket="golden",
                    request={"method": "GET", "path": "/health"},
                    expect={"status": 200, "json_contains": {"ok": True}},
                    visible=False,
                )
            )
            continue
        if any(k in low for k in ("never", "always", "must not", "invariant")) and any(
            x in low for x in ("health", "api", "json", "/api")
        ):
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.invariant,
                    bucket="invariant",
                    request={"method": "GET", "path": "/health"},
                    expect={"status": 200, "never_contains": ["traceback", "secret"]},
                    visible=False,
                )
            )
            continue
        if any(k in low for k in ("sql", "database", "postgres", "sqlite", "row count")):
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.db,
                    bucket="db",
                    request={"sql": "SELECT 1 AS ok", "dsn_env": "DATABASE_URL"},
                    expect={"row_count": 1},
                    visible=False,
                )
            )
            continue
        if any(k in low for k in ("aws ", "cli ", "json probe", "cloud")):
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.json_probe,
                    bucket="probe",
                    request={
                        "argv": [
                            "python3",
                            "-c",
                            "import json; print(json.dumps({'ok': True}))",
                        ]
                    },
                    expect={"exit_code": 0, "jsonpath_equals": {"ok": True}},
                    visible=False,
                )
            )
            continue
        if "health" in low and _HTTP.search(bullet) is None and "shows" not in low:
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.contract,
                    bucket="health",
                    request={"method": "GET", "path": "/health"},
                    expect={"status": 200, "json_contains": {"ok": True}},
                    visible=not cases,
                )
            )
            continue

        expect = _ui_expect(bullet)
        if expect is None:
            skipped.append(bullet)
            continue
        ui_path = "/"
        pm = re.search(r"(?i)\bat\s+(/\S+)", bullet)
        if pm:
            ui_path = pm.group(1).rstrip(".,)")
        cases.append(
            Case(
                id=cid,
                check=CheckMode.ui,
                bucket="ui",
                request={"path": ui_path},
                expect=expect,
                visible=not cases,
            )
        )

    for s in skipped:
        print(f"propose: skipped (need quoted text or text:/selector:): {s}", file=sys.stderr)
    if not cases:
        raise ValueError(
            'no draft cases — add Accept bullets with quoted UI text '
            '(e.g. shows "Get started") or HTTP paths'
        )
    if not any(c.visible for c in cases):
        cases[0].visible = True
    return card, cases


def load_fixture(name: str) -> tuple[TaskCard, list[Case]]:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", name or ""):
        raise ValueError(f"invalid fixture name: {name!r}")
    path = (_FIXTURES / f"{name}.json").resolve()
    if not path.is_relative_to(_FIXTURES.resolve()):
        raise ValueError(f"fixture escapes fixtures/: {name!r}")
    if not path.exists():
        raise FileNotFoundError(f"fixture not found: {path}")
    return import_cases_json(path)

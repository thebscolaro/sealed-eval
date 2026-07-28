from __future__ import annotations

import re
from pathlib import Path

from sealed_eval.capabilities import import_cases_json
from sealed_eval.models import Case, CheckMode, TaskCard

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"
_HTTP = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\s+(/\S+)", re.I)
_QUOTED = re.compile(r'["“]([^"”]+)["”]|\'([^\']+)\'')


def _ui_text(bullet: str) -> str:
    m = _QUOTED.search(bullet)
    if m:
        return next(g for g in m.groups() if g)
    for marker in ("shows ", "contain ", "contains ", "heading ", "title "):
        low = bullet.lower()
        idx = low.find(marker)
        if idx >= 0:
            rest = bullet[idx + len(marker) :].strip(" .")
            if rest:
                return rest.split()[0].strip(".,")
    caps = re.findall(r"\b([A-Z][A-Za-z0-9_-]{1,40})\b", bullet)
    return caps[-1] if caps else "App"


def propose_from_markdown(suite_id: str, title: str, body: str) -> tuple[TaskCard, list[Case]]:
    """Draft cases from AC bullets; operator must review then seal."""
    lines = [ln.strip("- ").strip() for ln in body.splitlines() if ln.strip()]
    ac: list[str] = []
    in_accept = False
    for ln in lines:
        low = ln.lower()
        if low.startswith("accept"):
            in_accept = True
            rest = ln.split(":", 1)[-1].strip() if ":" in ln else ""
            if rest:
                ac.append(rest)
            continue
        if in_accept or not any(x.lower().startswith("accept") for x in lines):
            if not low.startswith("title"):
                ac.append(ln)
    card = TaskCard(
        id=suite_id,
        title=title,
        summary=body.strip().splitlines()[0][:200] if body.strip() else title,
        public_acceptance=ac[:20] or ["behavior matches sealed corpus"],
    )
    cases: list[Case] = []
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
                    visible=("health" in path) or i == 0,
                )
            )
            continue
        if any(k in low for k in ("page", "button", "ui ", "browser", "click", "screenshot", "heading", "shows ")):
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.ui,
                    bucket="ui",
                    request={"path": "/"},
                    expect={"text": _ui_text(bullet)},
                    visible=i == 0,
                )
            )
            continue
        if any(k in low for k in ("golden", "matches fixture", "exact body", "sha256")) and "health" in low:
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
        if any(k in low for k in ("never", "always", "must not", "invariant", "property")) and any(
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
        if "health" in low:
            cases.append(
                Case(
                    id=cid,
                    check=CheckMode.contract,
                    bucket="health",
                    request={"method": "GET", "path": "/health"},
                    expect={"status": 200, "json_contains": {"ok": True}},
                    visible=i == 0,
                )
            )
            continue
        # default: UI text from bullet (SPA-friendly) — not a fake /health
        cases.append(
            Case(
                id=cid,
                check=CheckMode.ui,
                bucket="general",
                request={"path": "/"},
                expect={"text": _ui_text(bullet)},
                visible=i == 0,
            )
        )
    if not cases:
        cases = [
            Case(
                id="home",
                check=CheckMode.ui,
                bucket="ui",
                request={"path": "/"},
                expect={"text": "App"},
                visible=True,
            )
        ]
    return card, cases


def load_fixture(name: str) -> tuple[TaskCard, list[Case]]:
    path = _FIXTURES / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"fixture not found: {path}")
    return import_cases_json(path)

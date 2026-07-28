from __future__ import annotations

from pathlib import Path

from sealed_eval.capabilities import import_cases_json
from sealed_eval.models import Case, CheckMode, TaskCard

_FIXTURES = Path(__file__).resolve().parents[2] / "fixtures"


def propose_from_markdown(suite_id: str, title: str, body: str) -> tuple[TaskCard, list[Case]]:
    """Bullet lines after an Accept: header become public AC; else all bullets."""
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
    cases = [
        Case(
            id="health",
            check=CheckMode.contract,
            bucket="health",
            request={"method": "GET", "path": "/health"},
            expect={"status": 200, "json_contains": {"ok": True}},
            visible=True,
        )
    ]
    return card, cases


def load_fixture(name: str) -> tuple[TaskCard, list[Case]]:
    path = _FIXTURES / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"fixture not found: {path}")
    return import_cases_json(path)

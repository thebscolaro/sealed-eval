from __future__ import annotations

import shutil
from pathlib import Path

from sealed_eval.models import Case, TaskCard


def probe() -> dict[str, dict[str, bool | str]]:
    """Detect optional tools. No network auth probes beyond which(1)."""
    tools = {
        "gh": "GitHub CLI",
        "ctx7": "Context7 docs CLI",
        "docker": "Docker",
    }
    out: dict[str, dict[str, bool | str]] = {}
    for cmd, label in tools.items():
        path = shutil.which(cmd)
        out[cmd] = {"available": bool(path), "label": label, "path": path or ""}
    # intent-layer skill present?
    skill = Path.home() / ".agents" / "skills" / "intent-layer" / "SKILL.md"
    out["intent-layer"] = {
        "available": skill.exists(),
        "label": "intent-layer skill",
        "path": str(skill) if skill.exists() else "",
    }
    return out


def load_intent_layer_hints(subject_root: Path | None) -> list[str]:
    if not subject_root:
        return []
    hints: list[str] = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        p = subject_root / name
        if p.exists():
            hints.append(p.read_text(encoding="utf-8")[:4000])
    return hints


def import_cases_json(path: Path) -> tuple[TaskCard, list[Case]]:
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    card = TaskCard.model_validate(data["task_card"])
    cases = [Case.model_validate(c) for c in data["cases"]]
    return card, cases

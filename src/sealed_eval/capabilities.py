from __future__ import annotations

import shutil
from pathlib import Path

from sealed_eval.models import Case, TaskCard


def probe() -> dict[str, dict[str, bool | str]]:
    """Detect optional tools. No network auth probes beyond which(1)."""
    tools = {
        "gh": "GitHub CLI",
        "ctx7": "Context7 docs CLI",
        "ownlock": "ownlock secret broker",
    }
    out: dict[str, dict[str, bool | str]] = {}
    for cmd, label in tools.items():
        path = shutil.which(cmd)
        out[cmd] = {"available": bool(path), "label": label, "path": path or ""}

    podman = shutil.which("podman")
    docker = shutil.which("docker")
    runtime = "podman" if podman else ("docker" if docker else "")
    out["containers"] = {
        "available": bool(runtime),
        "label": "Podman or Docker (Dockerfile/compose names)",
        "path": (podman or docker or ""),
        "runtime": runtime,
    }
    # back-compat key for older scripts/docs
    out["docker"] = {
        "available": bool(docker or podman),
        "label": "Container runtime (docker|podman)",
        "path": docker or podman or "",
    }

    skill = Path.home() / ".agents" / "skills" / "intent-layer" / "SKILL.md"
    out["intent-layer"] = {
        "available": skill.exists(),
        "label": "intent-layer skill",
        "path": str(skill) if skill.exists() else "",
    }
    try:
        import playwright  # noqa: F401

        out["playwright"] = {"available": True, "label": "Playwright", "path": "python"}
    except ImportError:
        out["playwright"] = {"available": False, "label": "Playwright", "path": ""}
    return out


def import_cases_json(path: Path) -> tuple[TaskCard, list[Case]]:
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    card = TaskCard.model_validate(data["task_card"])
    cases = [Case.model_validate(c) for c in data["cases"]]
    return card, cases

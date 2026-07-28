from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

_SECTION = re.compile(
    r"(?im)^(#{1,3}\s*)?(accept(?:ance)?|criteria|requirements|definition of done)\b.*$"
)
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")
_AC_GLOBS = (
    "**/ACCEPT*.md",
    "**/Accept*.md",
    "**/acceptance*.md",
    "**/AC.md",
    "docs/**/*ac*.md",
    "docs/**/*accept*.md",
)


def _read(path: Path, limit: int = 80_000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _bullets_from_markdown(text: str, *, only_sections: bool) -> list[str]:
    lines = text.splitlines()
    out: list[str] = []
    in_sec = not only_sections
    for ln in lines:
        if _SECTION.match(ln.strip()):
            in_sec = True
            if ":" in ln:
                rest = ln.split(":", 1)[-1].strip()
                if rest and not rest.startswith("#"):
                    out.append(rest)
            continue
        if in_sec:
            m = _BULLET.match(ln)
            if m:
                out.append(m.group(1).strip())
            elif ln.strip().startswith("#") and only_sections:
                in_sec = False
    return out


def _dedupe(items: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for src, bullet in items:
        key = bullet.lower()
        if key in seen or len(bullet) < 3:
            continue
        seen.add(key)
        out.append((src, bullet))
    return out


def survey_subject(subject_path: Path) -> str:
    """Scan all seed sources; return markdown candidates + novel section. Never seals."""
    root = Path(subject_path).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"subject not found: {root}")

    found: list[tuple[str, str]] = []

    for pattern in _AC_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            for b in _bullets_from_markdown(_read(path), only_sections=False):
                found.append((str(path.relative_to(root)), b))

    for name in ("AGENTS.md", "CLAUDE.md"):
        p = root / name
        if p.is_file():
            for b in _bullets_from_markdown(_read(p), only_sections=False):
                found.append((name, b))

    doc_paths = [root / "README.md", root / "docs" / "RUNBOOK.md"]
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        doc_paths.extend(sorted(docs_dir.glob("*.md"))[:30])
    for p in doc_paths:
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        for b in _bullets_from_markdown(_read(p), only_sections=True):
            found.append((rel, b))
        if p.name == "README.md":
            for b in _bullets_from_markdown(_read(p), only_sections=False)[:15]:
                found.append((f"{rel}:bullet", b))

    if (root / ".git").exists():
        for kind, args in (
            ("issue", ["gh", "issue", "list", "--limit", "20", "--json", "title,number"]),
            ("pr", ["gh", "pr", "list", "--limit", "10", "--json", "title,number"]),
        ):
            try:
                raw = subprocess.check_output(
                    args, cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=15
                )
                for row in json.loads(raw or "[]"):
                    title = (row.get("title") or "").strip()
                    num = row.get("number")
                    if title:
                        found.append((f"gh:{kind}#{num}", title))
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                pass

    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(_read(pkg))
            for name in data.get("scripts") or {}:
                found.append(("package.json:scripts", f'heuristic: npm script "{name}" exists'))
        except json.JSONDecodeError:
            pass

    for sub in ("src/views", "src/pages", "src/components", "src/routes"):
        d = root / sub
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*"))[:40]:
            if path.suffix.lower() in {".vue", ".tsx", ".jsx"} and path.is_file():
                found.append(
                    (
                        f"heuristic:{path.relative_to(root)}",
                        f'UI page/component "{path.stem}" is present',
                    )
                )

    found = _dedupe(found)[:40]

    lines = [
        "# Survey candidates",
        "",
        f"Subject: `{root}`",
        "",
        "Auto-scanned all seed sources. Edit freely, then fill Accept (approved).",
        "**Do not seal until a human OK's this list.**",
        "",
        "## From repository / tools",
        "",
    ]
    if not found:
        lines.append("- _(no candidates found — fill Novel acceptance below)_")
    for src, bullet in found:
        lines.append(f"- {bullet} _(source: {src})_")

    lines.extend(
        [
            "",
            "## Novel acceptance (human)",
            "",
            "Add bullets **not** covered above. UI expects need quoted text,",
            'e.g. `Landing shows "Get started"`.',
            "",
            "- ",
            "",
            "## Accept (approved)",
            "",
            "After human review, paste final clean bullets here (no source tags):",
            "",
            "Accept:",
            "- ",
        ]
    )
    return "\n".join(lines) + "\n"

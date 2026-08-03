from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

_SECTION = re.compile(
    r"(?im)^(#{1,3}\s*)?(accept(?:ance)?|criteria|requirements|definition of done)\b.*$"
)
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")
_GH_NOISE = re.compile(
    r"(?i)\b(dependabot|renovate)\b|\bchore\s*\(\s*deps|\bbump\s+|deps?-dev|deps?-prod|"
    r"^⬆\s*update\b|\brequirement from\b"
)
_AC_GLOBS = (
    "**/ACCEPT*.md",
    "**/Accept*.md",
    "**/acceptance*.md",
    "**/AC.md",
    "**/*criteria*.md",
    "docs/**/*accept*.md",
    "docs/**/*criteria*.md",
    "docs/defects/**/*.md",
)
_PRIMARY_CAP = 25
_HEURISTIC_CAP = 15
_HEURISTIC_SCRIPTS = frozenset({"test", "lint", "build", "check", "typecheck"})


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


def _is_gh_noise(title: str) -> bool:
    return bool(_GH_NOISE.search(title))


def survey_subject(subject_path: Path) -> str:
    """Scan all seed sources; return markdown candidates + novel section. Never seals."""
    root = Path(subject_path).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"subject not found: {root}")

    primary: list[tuple[str, str]] = []
    heuristics: list[tuple[str, str]] = []

    for pattern in _AC_GLOBS:
        for path in root.glob(pattern):
            if not path.is_file():
                continue
            # Example-run dumps are agent transcripts, not AC seeds
            if "example-runs" in path.parts:
                continue
            rel = str(path.relative_to(root))
            # Defect writeups: prefer Accept/Criteria sections; else first few bullets only
            only_sec = "defects" in path.parts
            bullets = _bullets_from_markdown(_read(path), only_sections=only_sec)
            if only_sec and not bullets:
                bullets = _bullets_from_markdown(_read(path), only_sections=False)[:5]
            for b in bullets:
                primary.append((rel, b))

    for name in ("AGENTS.md", "CLAUDE.md"):
        p = root / name
        if p.is_file():
            for b in _bullets_from_markdown(_read(p), only_sections=True):
                primary.append((name, b))

    doc_paths = [root / "README.md", root / "docs" / "RUNBOOK.md"]
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        doc_paths.extend(sorted(docs_dir.rglob("*.md"))[:40])
    seen_docs: set[Path] = set()
    for p in doc_paths:
        if not p.is_file() or p in seen_docs:
            continue
        seen_docs.add(p)
        rel = str(p.relative_to(root))
        # Accept/Criteria sections only — no README feature-bullet dump
        for b in _bullets_from_markdown(_read(p), only_sections=True):
            primary.append((rel, b))

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
                    if not title or _is_gh_noise(title):
                        continue
                    if kind == "pr" and re.match(r"(?i)^(chore|build|ci|docs)(\(|:|\s)", title):
                        continue
                    primary.append((f"gh:{kind}#{num}", title))
            except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                pass

    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(_read(pkg))
            for name in data.get("scripts") or {}:
                if name in _HEURISTIC_SCRIPTS or name.startswith("test"):
                    heuristics.append(
                        ("package.json:scripts", f'heuristic: npm script "{name}" exists')
                    )
        except json.JSONDecodeError:
            pass

    for sub in ("src/views", "src/pages", "src/components", "src/routes", "web/src"):
        d = root / sub
        if not d.is_dir():
            continue
        for path in sorted(d.rglob("*"))[:10]:
            if path.suffix.lower() in {".vue", ".tsx", ".jsx"} and path.is_file():
                heuristics.append(
                    (
                        f"heuristic:{path.relative_to(root)}",
                        f'UI page/component "{path.stem}" is present',
                    )
                )

    primary = _dedupe(primary)[:_PRIMARY_CAP]
    heuristics = _dedupe(heuristics)[:_HEURISTIC_CAP]

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
    if not primary:
        lines.append("- _(no candidates found — fill Novel acceptance below)_")
    for src, bullet in primary:
        lines.append(f"- {bullet} _(source: {src})_")

    lines.extend(["", "## Low-confidence heuristics", ""])
    if not heuristics:
        lines.append("- _(none)_")
    else:
        for src, bullet in heuristics:
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

from __future__ import annotations

from pathlib import Path

import typer
import uvicorn

from sealed_eval.capabilities import probe
from sealed_eval.grader import grade_artifact
from sealed_eval.propose import load_fixture, propose_from_markdown
from sealed_eval.store import SealedStore

app = typer.Typer(help="SEALed-eval CLI", no_args_is_help=True)


def _store(path: Path | None) -> SealedStore:
    root = path or (Path(__file__).resolve().parents[2] / "sealed")
    return SealedStore(root)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8787):
    uvicorn.run("sealed_eval.api:app", host=host, port=port, reload=False)


@app.command("propose")
def propose_cmd(
    suite_id: str,
    title: str = "Untitled",
    markdown_file: Path | None = None,
    fixture: str | None = None,
    import_path: Path | None = None,
    store_path: Path | None = None,
):
    from sealed_eval.capabilities import import_cases_json

    store = _store(store_path)
    if import_path:
        card, cases = import_cases_json(import_path)
        card.id = suite_id or card.id
    elif fixture:
        card, cases = load_fixture(fixture)
        card.id = suite_id or card.id
    else:
        body = markdown_file.read_text(encoding="utf-8") if markdown_file else title
        card, cases = propose_from_markdown(suite_id, title, body)
    store.write_draft(card, cases)
    typer.echo(f"draft {card.id} cases={len(cases)}")


@app.command("show-draft")
def show_draft(suite_id: str, store_path: Path | None = None):
    import json

    cases = _store(store_path).load_draft_cases(suite_id)
    typer.echo(json.dumps([c.model_dump(mode="json") for c in cases], indent=2))


@app.command()
def seal(suite_id: str, token: str, store_path: Path | None = None):
    s = _store(store_path).seal_corpus(suite_id, token)
    typer.echo(s)


@app.command()
def publish(suite_id: str, out: Path | None = None, store_path: Path | None = None):
    import json

    task = _store(store_path).public_task(suite_id)
    text = json.dumps(task, indent=2)
    if out:
        out.write_text(text, encoding="utf-8")
    typer.echo(text)


@app.command()
def grade(
    suite_id: str,
    artifact_url: str,
    token: str,
    store_path: Path | None = None,
    pass_threshold: float = 1.0,
    max_gap: float = 0.25,
):
    import json

    score = grade_artifact(
        _store(store_path),
        suite_id,
        artifact_url,
        token,
        pass_threshold=pass_threshold,
        max_gap=max_gap,
    )
    typer.echo(json.dumps(score.model_dump(), indent=2))
    raise SystemExit(0 if score.passed else 1)


@app.command()
def scorecard(suite_id: str, store_path: Path | None = None, out: Path | None = None):
    """Coder-safe aggregate scorecard (no seal token)."""
    import json

    data = _store(store_path).load_public_scorecard(suite_id)
    text = json.dumps(data, indent=2)
    if out:
        out.write_text(text, encoding="utf-8")
    typer.echo(text)


@app.command()
def capabilities():
    import json

    typer.echo(json.dumps(probe(), indent=2))


@app.command("new-token")
def new_token():
    typer.echo(SealedStore.new_token())


@app.command("survey-subject")
def survey_subject_cmd(
    subject_path: Path,
    out: Path | None = None,
):
    """Scan subject for AC seeds (all sources). Draft only — never seals."""
    from sealed_eval.survey import survey_subject

    text = survey_subject(subject_path)
    if out:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        typer.echo(f"wrote {out}")
    typer.echo(text)


if __name__ == "__main__":
    app()

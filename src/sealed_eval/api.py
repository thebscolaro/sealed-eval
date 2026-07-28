from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from sealed_eval.capabilities import import_cases_json, probe
from sealed_eval.grader import apply_gate, grade_artifact
from sealed_eval.propose import load_fixture, propose_from_markdown
from sealed_eval.store import SealedStore

app = FastAPI(title="SEALed-eval", version="0.3.1")


def _store() -> SealedStore:
    root = Path(__file__).resolve().parents[2] / "sealed"
    return SealedStore(root)


class ProposeBody(BaseModel):
    suite_id: str
    title: str = "Untitled"
    markdown: str = ""
    fixture: str | None = None
    import_path: str | None = None


class SealBody(BaseModel):
    suite_id: str
    token: str


class ArtifactBody(BaseModel):
    suite_id: str
    artifact_base_url: str


class GradeBody(BaseModel):
    suite_id: str
    artifact_base_url: str | None = None
    token: str
    pass_threshold: float = Field(default=1.0, ge=0.0, le=1.0)
    max_gap: float = Field(default=0.25, ge=0.0, le=1.0)


class GateBody(BaseModel):
    suite_id: str
    ok: int
    total: int
    pass_threshold: float = Field(default=1.0, ge=0.0, le=1.0)
    visible_heldout_gap: float = 0.0
    max_gap: float = 0.25


@app.get("/health")
def health():
    return {"ok": True, "service": "sealed-eval"}


@app.get("/v1/capabilities")
def capabilities():
    return probe()


@app.post("/v1/propose_eval")
def propose_eval(body: ProposeBody):
    store = _store()
    try:
        if body.import_path:
            card, cases = import_cases_json(Path(body.import_path))
            card.id = body.suite_id or card.id
        elif body.fixture:
            card, cases = load_fixture(body.fixture)
            card.id = body.suite_id or card.id
        else:
            card, cases = propose_from_markdown(body.suite_id, body.title, body.markdown)
            card.id = body.suite_id
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    store.write_draft(card, cases)
    return {"status": "draft", "suite_id": card.id, "cases": len(cases)}


@app.get("/v1/draft/{suite_id}")
def draft(suite_id: str, x_seal_token: str | None = Header(default=None), token: str | None = None):
    """Operator-only: draft includes expects. Require any shared operator token later;
    for now require X-Seal-Token or ?token= matching a sealed suite OR presence of draft-only
    operator header SE-Operator. ponytail: if suite not sealed yet, require SE-Operator: 1.
    """
    store = _store()
    try:
        cases = store.load_draft_cases(suite_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    sealed = (store._suite_dir(suite_id) / "cases.sealed.json").exists()
    if sealed:
        tok = token or x_seal_token
        if not tok:
            raise HTTPException(401, "seal token required for sealed suite draft")
        try:
            store.require_seal(suite_id, tok)
        except PermissionError as e:
            raise HTTPException(403, str(e)) from e
    # unsealed draft: local demo only — do not expose serve to coder networks
    return {"suite_id": suite_id, "cases": [c.model_dump(mode="json") for c in cases]}


@app.post("/v1/seal_corpus")
def seal_corpus(body: SealBody):
    store = _store()
    try:
        seal = store.seal_corpus(body.suite_id, body.token)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    return {"status": "sealed", "suite_id": body.suite_id, "seal": seal}


@app.post("/v1/publish_task")
def publish_task(suite_id: str):
    store = _store()
    try:
        return store.public_task(suite_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.get("/v1/public_task/{suite_id}")
def public_task(suite_id: str):
    return publish_task(suite_id)


@app.post("/v1/submit_artifact")
def submit_artifact(body: ArtifactBody):
    store = _store()
    try:
        store.register_artifact(body.suite_id, body.artifact_base_url)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    return {"status": "registered", "suite_id": body.suite_id}


@app.post("/v1/grade")
def grade(body: GradeBody, x_seal_token: str | None = Header(default=None)):
    token = body.token or x_seal_token
    if not token:
        raise HTTPException(401, "seal token required")
    store = _store()
    url = body.artifact_base_url or store.artifact_url(body.suite_id)
    if not url:
        raise HTTPException(400, "artifact_base_url required (or submit_artifact first)")
    try:
        score = grade_artifact(
            store,
            body.suite_id,
            url,
            token,
            pass_threshold=body.pass_threshold,
            max_gap=body.max_gap,
        )
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    return score.model_dump()


@app.get("/v1/scorecard/{suite_id}")
def scorecard(suite_id: str):
    """Coder-safe aggregates; no seal token."""
    try:
        return _store().load_public_scorecard(suite_id)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e


@app.post("/v1/gate")
def gate(body: GateBody):
    from sealed_eval.models import Scorecard

    score = Scorecard(
        suite_id=body.suite_id,
        passed=False,
        total=body.total,
        ok=body.ok,
        visible_heldout_gap=body.visible_heldout_gap,
    )
    score = apply_gate(score, pass_threshold=body.pass_threshold, max_gap=body.max_gap)
    rate = (body.ok / body.total) if body.total else 0.0
    return {"suite_id": body.suite_id, "gate": score.gate, "rate": rate}

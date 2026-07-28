from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from sealed_eval.capabilities import import_cases_json, probe
from sealed_eval.grader import grade_artifact
from sealed_eval.propose import load_fixture, propose_from_markdown
from sealed_eval.store import SealedStore

app = FastAPI(title="SEALed-eval", version="0.1.0")


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
        score = grade_artifact(store, body.suite_id, url, token)
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except FileNotFoundError as e:
        raise HTTPException(404, str(e)) from e
    rate = (score.ok / score.total) if score.total else 0.0
    if rate >= body.pass_threshold and score.visible_heldout_gap <= 0.25:
        score.gate = "pass"
        score.passed = True
    elif rate >= body.pass_threshold * 0.8:
        score.gate = "retry"
        score.passed = False
    else:
        score.gate = "fail"
        score.passed = False
    return score.model_dump()


@app.post("/v1/gate")
def gate(body: GateBody):
    rate = (body.ok / body.total) if body.total else 0.0
    if rate >= body.pass_threshold and body.visible_heldout_gap <= body.max_gap:
        decision = "pass"
    elif rate >= body.pass_threshold * 0.8:
        decision = "retry"
    else:
        decision = "fail"
    return {"suite_id": body.suite_id, "gate": decision, "rate": rate}

from __future__ import annotations

import threading
import time
from pathlib import Path

import httpx
import uvicorn

from sealed_eval.grader import grade_artifact
from sealed_eval.propose import load_fixture
from sealed_eval.store import SealedStore


def _serve(app, host: str, port: int):
    uvicorn.run(app, host=host, port=port, log_level="error")


def test_e2e_orders_pass(tmp_path: Path):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "subject-demo"))
    from app import app as subject_app  # noqa: WPS433

    import socket

    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    t = threading.Thread(target=_serve, args=(subject_app, "127.0.0.1", port), daemon=True)
    t.start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            httpx.get(base + "/health", timeout=0.2).raise_for_status()
            break
        except Exception:
            time.sleep(0.05)
    else:
        raise RuntimeError("subject failed to start")

    store = SealedStore(tmp_path)
    card, cases = load_fixture("orders")
    store.write_draft(card, cases)
    token = "demo-seal-token"
    store.seal_corpus(card.id, token)
    store.register_artifact(card.id, base)
    score = grade_artifact(store, card.id, base, token)
    assert score.passed, score.model_dump()
    assert score.gate == "pass"
    assert score.visible_heldout_gap == 0.0

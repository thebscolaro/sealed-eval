from pathlib import Path

from sealed_eval.models import Case, CheckMode, TaskCard
from sealed_eval.store import SealedStore


def test_seal_and_grade_contract(tmp_path: Path):
    store = SealedStore(tmp_path)
    card = TaskCard(
        id="orders-v1",
        title="Orders API",
        summary="Create and fetch orders",
        public_acceptance=["POST /orders returns 201", "GET /orders/{id} returns order"],
    )
    cases = [
        Case(
            id="create-order",
            check=CheckMode.contract,
            bucket="orders",
            request={"method": "POST", "path": "/orders", "json": {"sku": "abc", "qty": 2}},
            expect={"status": 201, "json_contains": {"sku": "abc", "qty": 2}},
        ),
        Case(
            id="get-order",
            check=CheckMode.contract,
            bucket="orders",
            request={"method": "GET", "path": "/orders/{last_id}"},
            expect={"status": 200, "json_contains": {"sku": "abc"}},
        ),
    ]
    store.write_draft(card, cases)
    seal = store.seal_corpus("orders-v1", token="test-seal-token")
    assert seal.startswith("seal_")

    from sealed_eval.grader import grade_artifact

    score = grade_artifact(
        store,
        suite_id="orders-v1",
        artifact_base_url="http://127.0.0.1:0",
        seal_token="test-seal-token",
    )
    assert score.passed is False
    assert score.total == 2
    assert "orders" in score.buckets


def test_load_cases_requires_seal(tmp_path: Path):
    store = SealedStore(tmp_path)
    card = TaskCard(id="x", title="t", summary="s")
    store.write_draft(card, [])
    try:
        store.load_cases("x")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError:
        pass

from __future__ import annotations

from typing import Any

import httpx

from sealed_eval.models import Case


def run_contract(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    req = case.request
    method = req.get("method", "GET").upper()
    path = req.get("path", "/")
    for k, v in ctx.items():
        path = path.replace("{" + k + "}", str(v))
    url = base_url.rstrip("/") + path
    headers = req.get("headers") or {}
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.request(method, url, json=req.get("json"), headers=headers)
    except Exception as e:  # noqa: BLE001 — grade as fail bucket
        return False, f"request_error:{type(e).__name__}"

    expect = case.expect
    if r.status_code != expect.get("status", 200):
        return False, f"status:{r.status_code}"
    want = expect.get("json_contains")
    body: dict[str, Any] | None = None
    if want is not None or expect.get("capture_id", True):
        try:
            parsed = r.json()
            body = parsed if isinstance(parsed, dict) else None
        except Exception:
            if want is not None:
                return False, "bad_json"
            body = None
    if want and body is not None:
        for k, v in want.items():
            if body.get(k) != v:
                return False, f"field:{k}"
    if body is not None and expect.get("capture_id", True):
        if "id" in body:
            ctx["last_id"] = body["id"]
        entry = body.get("entry")
        if isinstance(entry, dict) and "id" in entry:
            ctx["last_id"] = entry["id"]
    return True, "ok"

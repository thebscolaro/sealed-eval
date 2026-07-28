from __future__ import annotations

import hashlib
import json
import re
import subprocess
from typing import Any

import httpx

from sealed_eval.models import Case


def _subst(path: str, ctx: dict[str, Any]) -> str:
    for k, v in ctx.items():
        path = path.replace("{" + k + "}", str(v))
    return path


def _jsonpath_get(data: Any, path: str) -> Any:
    """Tiny dotted/bracket path: a.b[0].c — ponytail: not full JSONPath."""
    cur = data
    for part in path.replace("[", ".").replace("]", "").split("."):
        if part == "":
            continue
        if isinstance(cur, list):
            cur = cur[int(part)]
        elif isinstance(cur, dict):
            cur = cur[part]
        else:
            raise KeyError(path)
    return cur


def _capture_ids(body: dict[str, Any], ctx: dict[str, Any], expect: dict[str, Any]) -> None:
    if not expect.get("capture_id", True):
        return
    if "id" in body:
        ctx["last_id"] = body["id"]
    entry = body.get("entry")
    if isinstance(entry, dict) and "id" in entry:
        ctx["last_id"] = entry["id"]


def _http(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[httpx.Response | None, str]:
    req = case.request
    method = req.get("method", "GET").upper()
    path = _subst(req.get("path", "/"), ctx)
    url = base_url.rstrip("/") + path
    headers = dict(req.get("headers") or {})
    try:
        with httpx.Client(timeout=float(req.get("timeout", 5.0))) as client:
            return client.request(method, url, json=req.get("json"), headers=headers), "ok"
    except Exception as e:  # noqa: BLE001
        return None, f"request_error:{type(e).__name__}"


def run_contract(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    r, err = _http(case, base_url, ctx)
    if r is None:
        return False, err
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
    if body is not None:
        _capture_ids(body, ctx, expect)
    return True, "ok"


def _check_predicates(body: Any, text: str, expect: dict[str, Any]) -> tuple[bool, str]:
    if "sha256" in expect:
        dig = hashlib.sha256(
            text.encode() if isinstance(text, str) else json.dumps(body, sort_keys=True).encode()
        ).hexdigest()
        if dig != expect["sha256"]:
            return False, "sha256_mismatch"
    if "json_equals" in expect:
        if body != expect["json_equals"]:
            return False, "json_equals"
    if "json_contains" in expect and isinstance(body, dict):
        for k, v in expect["json_contains"].items():
            if body.get(k) != v:
                return False, f"field:{k}"
    for jp, want in (expect.get("jsonpath_equals") or {}).items():
        try:
            got = _jsonpath_get(body, jp)
        except Exception:
            return False, f"jsonpath_missing:{jp}"
        if got != want:
            return False, f"jsonpath:{jp}"
    if "regex" in expect:
        if not re.search(expect["regex"], text if isinstance(text, str) else json.dumps(body)):
            return False, "regex"
    for s in expect.get("never_contains") or []:
        hay = text if isinstance(text, str) else json.dumps(body)
        if str(s) in hay:
            return False, f"never_contains:{s}"
    if "min_length" in expect and len(text) < int(expect["min_length"]):
        return False, "min_length"
    return True, "ok"


def run_holdout_golden(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    """HTTP (or static) body vs sealed expected / hash."""
    if case.request.get("path"):
        r, err = _http(case, base_url, ctx)
        if r is None:
            return False, err
        expect = case.expect
        if "status" in expect and r.status_code != expect["status"]:
            return False, f"status:{r.status_code}"
        try:
            body = r.json()
            text = r.text
        except Exception:
            body = None
            text = r.text
        if isinstance(body, dict):
            _capture_ids(body, ctx, expect)
        return _check_predicates(body, text, expect)
    # file golden under request.file (relative path resolved by caller via request)
    path = case.request.get("file")
    if not path:
        return False, "no_target"
    try:
        raw = open(path, encoding="utf-8").read()  # noqa: PTH123 — sealed path from case
    except OSError:
        return False, "file_missing"
    try:
        body = json.loads(raw)
    except Exception:
        body = None
    return _check_predicates(body, raw, case.expect)


def run_invariant(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    """Property checks on an HTTP response (or last body in ctx)."""
    if case.request.get("path"):
        r, err = _http(case, base_url, ctx)
        if r is None:
            return False, err
        if "status" in case.expect and r.status_code != case.expect["status"]:
            return False, f"status:{r.status_code}"
        try:
            body = r.json()
        except Exception:
            body = None
        text = r.text
        if isinstance(body, dict):
            _capture_ids(body, ctx, case.expect)
        return _check_predicates(body, text, case.expect)
    body = ctx.get("last_body")
    text = ctx.get("last_text", json.dumps(body) if body is not None else "")
    return _check_predicates(body, text, case.expect)


def run_json_probe(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    """Run sealed argv; assert JSON stdout. base_url unused; env from ownlock run."""
    del base_url
    argv = case.request.get("argv") or []
    if not argv:
        return False, "no_argv"
    try:
        proc = subprocess.run(  # noqa: S603 — sealed argv from operator corpus
            [str(a) for a in argv],
            capture_output=True,
            text=True,
            timeout=float(case.request.get("timeout", 30)),
            check=False,
        )
    except Exception as e:  # noqa: BLE001
        return False, f"probe_error:{type(e).__name__}"
    if "exit_code" in case.expect and proc.returncode != case.expect["exit_code"]:
        return False, f"exit:{proc.returncode}"
    try:
        body = json.loads(proc.stdout or "null")
    except Exception:
        return False, "bad_json"
    return _check_predicates(body, proc.stdout or "", case.expect)


def run_db(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    """Read-only SQL via DATABASE_URL (or request.dsn_env)."""
    del base_url, ctx
    import os

    env_key = case.request.get("dsn_env", "DATABASE_URL")
    dsn = os.environ.get(env_key)
    if not dsn:
        return False, f"missing_env:{env_key}"
    sql = case.request.get("sql")
    if not sql:
        return False, "no_sql"
    low = sql.strip().lower()
    if not low.startswith("select") and not low.startswith("with"):
        return False, "not_readonly"
    try:
        import sqlite3
        from urllib.parse import urlparse

        u = urlparse(dsn)
        if u.scheme in ("sqlite", "sqlite3", ""):
            path = u.path if u.scheme else dsn
            if path.startswith("//"):
                path = path[1:]
            conn = sqlite3.connect(path)
            conn.row_factory = sqlite3.Row
            rows = [dict(r) for r in conn.execute(sql).fetchall()]
            conn.close()
        else:
            # ponytail: optional psycopg only if installed
            try:
                import psycopg

                with psycopg.connect(dsn) as conn:
                    with conn.cursor() as cur:
                        cur.execute(sql)
                        cols = [d.name for d in cur.description] if cur.description else []
                        rows = [dict(zip(cols, row, strict=False)) for row in cur.fetchall()]
            except ImportError:
                return False, "psycopg_missing"
    except Exception as e:  # noqa: BLE001
        return False, f"db_error:{type(e).__name__}"
    expect = case.expect
    if "row_count" in expect and len(rows) != int(expect["row_count"]):
        return False, f"row_count:{len(rows)}"
    if "row0_contains" in expect and rows:
        for k, v in expect["row0_contains"].items():
            if rows[0].get(k) != v:
                return False, f"row0:{k}"
    return True, "ok"


def run_ui(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    """Playwright text/selector/screenshot asserts against base_url + path."""
    del ctx
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False, "playwright_missing"
    path = case.request.get("path", "/")
    url = base_url.rstrip("/") + path
    expect = case.expect
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            html = page.content()
            if "text" in expect and expect["text"] not in html:
                browser.close()
                return False, "text_missing"
            for s in expect.get("never_contains") or []:
                if str(s) in html:
                    browser.close()
                    return False, f"never_contains:{s}"
            if "selector" in expect:
                loc = page.locator(expect["selector"])
                if loc.count() < 1:
                    browser.close()
                    return False, "selector_missing"
                if "selector_text" in expect and expect["selector_text"] not in (
                    loc.first.text_content() or ""
                ):
                    browser.close()
                    return False, "selector_text"
            if "screenshot_sha256" in expect:
                dig = hashlib.sha256(page.screenshot(full_page=True)).hexdigest()
                if dig != expect["screenshot_sha256"]:
                    browser.close()
                    return False, "screenshot_sha256"
            browser.close()
    except Exception as e:  # noqa: BLE001
        return False, f"ui_error:{type(e).__name__}"
    return True, "ok"


def run_case(case: Case, base_url: str, ctx: dict[str, Any]) -> tuple[bool, str]:
    from sealed_eval.models import CheckMode

    dispatch = {
        CheckMode.contract: run_contract,
        CheckMode.holdout_golden: run_holdout_golden,
        CheckMode.invariant: run_invariant,
        CheckMode.json_probe: run_json_probe,
        CheckMode.db: run_db,
        CheckMode.ui: run_ui,
    }
    fn = dispatch.get(case.check)
    if not fn:
        return False, "unsupported_check"
    return fn(case, base_url, ctx)

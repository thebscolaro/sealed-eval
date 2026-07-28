#!/usr/bin/env bash
# SQLite db check + json_probe smoke.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck disable=SC1091
source .venv/bin/activate
SUITE="probe-db-demo"
rm -rf "sealed/${SUITE}"
DB="$(mktemp /tmp/se-db.XXXXXX)"
export DATABASE_URL="sqlite:///$DB"
export SE_SUITE="$SUITE"
export SE_DB="$DB"
python3 <<'PY'
import json, os, pathlib, sqlite3, subprocess

db = os.environ["SE_DB"]
suite = os.environ["SE_SUITE"]
c = sqlite3.connect(db)
c.execute("create table t(id int)")
c.execute("insert into t values (1)")
c.commit()
c.close()

fixture = pathlib.Path("/tmp/se-probe-db.json")
fixture.write_text(
    json.dumps(
        {
            "task_card": {
                "id": suite,
                "title": "probe-db",
                "summary": "json_probe and db",
                "public_acceptance": ["probe and db"],
            },
            "cases": [
                {
                    "id": "probe",
                    "check": "json_probe",
                    "bucket": "probe",
                    "request": {
                        "argv": [
                            "python3",
                            "-c",
                            "import json; print(json.dumps({'ok': True}))",
                        ]
                    },
                    "expect": {"exit_code": 0, "jsonpath_equals": {"ok": True}},
                    "visible": True,
                },
                {
                    "id": "db",
                    "check": "db",
                    "bucket": "db",
                    "request": {"sql": "SELECT id FROM t", "dsn_env": "DATABASE_URL"},
                    "expect": {"row_count": 1, "row0_contains": {"id": 1}},
                    "visible": False,
                },
            ],
        },
        indent=2,
    ),
    encoding="utf-8",
)

token = subprocess.check_output(["sealed-eval", "new-token"], text=True).strip()
subprocess.check_call(["sealed-eval", "propose", suite, "--import-path", str(fixture)])
subprocess.check_call(["sealed-eval", "seal", suite, token], stdout=subprocess.DEVNULL)
raise SystemExit(
    subprocess.run(
        ["sealed-eval", "grade", suite, "http://127.0.0.1:9", token], check=False
    ).returncode
)
PY
EC=$?
rm -f "$DB"
if [[ "$EC" -ne 0 ]]; then
  echo "dogfood-probe-db: failed" >&2
  exit "$EC"
fi
echo "dogfood-probe-db: OK"

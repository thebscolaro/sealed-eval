from __future__ import annotations

import hashlib
import json
import secrets
from pathlib import Path

from sealed_eval.models import Case, SuiteStatus, TaskCard


class SealedStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _suite_dir(self, suite_id: str) -> Path:
        return self.root / suite_id

    def write_draft(self, card: TaskCard, cases: list[Case]) -> None:
        d = self._suite_dir(card.id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "task_card.json").write_text(card.model_dump_json(indent=2), encoding="utf-8")
        payload = [c.model_dump(mode="json") for c in cases]
        (d / "cases.draft.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (d / "status").write_text(SuiteStatus.draft.value, encoding="utf-8")

    def seal_corpus(self, suite_id: str, token: str) -> str:
        d = self._suite_dir(suite_id)
        draft = d / "cases.draft.json"
        if not draft.exists():
            raise FileNotFoundError(f"no draft for {suite_id}")
        raw = draft.read_bytes()
        digest = hashlib.sha256(raw + token.encode()).hexdigest()
        seal = f"seal_{digest[:24]}"
        (d / "cases.sealed.json").write_bytes(raw)
        (d / "seal").write_text(seal, encoding="utf-8")
        (d / "status").write_text(SuiteStatus.sealed.value, encoding="utf-8")
        # ponytail: plaintext expecteds ok for local demo; hash-expected later
        return seal

    def require_seal(self, suite_id: str, token: str) -> None:
        d = self._suite_dir(suite_id)
        expected = (d / "seal").read_text(encoding="utf-8").strip()
        draft = (d / "cases.sealed.json").read_bytes()
        digest = hashlib.sha256(draft + token.encode()).hexdigest()
        got = f"seal_{digest[:24]}"
        if got != expected:
            raise PermissionError("seal token mismatch")

    def load_task(self, suite_id: str) -> TaskCard:
        return TaskCard.model_validate_json(
            (self._suite_dir(suite_id) / "task_card.json").read_text(encoding="utf-8")
        )

    def load_cases(self, suite_id: str) -> list[Case]:
        path = self._suite_dir(suite_id) / "cases.sealed.json"
        if not path.exists():
            raise FileNotFoundError(f"suite {suite_id} not sealed")
        data = json.loads(path.read_text(encoding="utf-8"))
        return [Case.model_validate(x) for x in data]

    def register_artifact(self, suite_id: str, artifact_base_url: str) -> None:
        d = self._suite_dir(suite_id)
        if not (d / "cases.sealed.json").exists():
            raise FileNotFoundError(f"suite {suite_id} not sealed")
        (d / "artifact.url").write_text(artifact_base_url.strip(), encoding="utf-8")

    def artifact_url(self, suite_id: str) -> str | None:
        p = self._suite_dir(suite_id) / "artifact.url"
        return p.read_text(encoding="utf-8").strip() if p.exists() else None

    def public_task(self, suite_id: str) -> dict:
        card = self.load_task(suite_id)
        return card.model_dump()

    @staticmethod
    def new_token() -> str:
        return secrets.token_urlsafe(24)

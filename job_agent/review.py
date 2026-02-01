from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from job_agent.interfaces import DraftMessage, ReviewQueue
from job_agent.storage import JsonJobRepository


@dataclass
class LocalReviewQueue(ReviewQueue):
    """Simple review queue that writes drafts to disk for manual approval."""

    drafts_dir: Path
    repository: JsonJobRepository

    def request_review(self, job_id: str, draft: DraftMessage) -> None:
        self.drafts_dir.mkdir(parents=True, exist_ok=True)
        draft_path = self.drafts_dir / f"{job_id}.md"
        draft_path.write_text(
            f"# {draft.subject}\n\n{draft.body}\n",
            encoding="utf-8",
        )

    def is_approved(self, job_id: str) -> bool:
        data = self.repository._load()
        return bool(data["jobs"].get(job_id, {}).get("approved"))

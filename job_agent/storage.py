from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from job_agent.interfaces import JobLink, JobRepository


@dataclass
class JsonJobRepository(JobRepository):
    """Lightweight JSON-backed repository for local design iterations."""

    path: Path

    def add_job_link(self, link: JobLink) -> str:
        data = self._load()
        job_id = f"job-{len(data['jobs']) + 1}"
        data["jobs"][job_id] = {"url": link.url, "source": link.source, "approved": False}
        self._save(data)
        return job_id

    def list_pending_jobs(self) -> Iterable[str]:
        data = self._load()
        return [job_id for job_id, payload in data["jobs"].items() if not payload["approved"]]

    def mark_approved(self, job_id: str) -> None:
        data = self._load()
        if job_id not in data["jobs"]:
            raise KeyError(f"Unknown job id: {job_id}")
        data["jobs"][job_id]["approved"] = True
        self._save(data)

    def _load(self) -> dict:
        if not self.path.exists():
            return {"jobs": {}}
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")

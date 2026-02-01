from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol


@dataclass(frozen=True)
class JobLink:
    url: str
    source: str


@dataclass(frozen=True)
class DraftMessage:
    subject: str
    body: str


class JobRepository(Protocol):
    def add_job_link(self, link: JobLink) -> str:
        """Persist a job link and return the job ID."""

    def list_pending_jobs(self) -> Iterable[str]:
        """Return job IDs awaiting review."""

    def mark_approved(self, job_id: str) -> None:
        """Mark a job application as approved."""


class ReviewQueue(Protocol):
    def request_review(self, job_id: str, draft: DraftMessage) -> None:
        """Queue a draft for human approval."""

    def is_approved(self, job_id: str) -> bool:
        """Check whether a job application is approved."""


class OpenClawRuntime(Protocol):
    def start(self) -> None:
        """Start the local OpenClaw runtime."""

    def stop(self) -> None:
        """Stop the local OpenClaw runtime."""

    def generate_outreach(self, job_id: str) -> DraftMessage:
        """Create a connection email or cover letter draft."""

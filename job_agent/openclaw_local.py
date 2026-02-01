from __future__ import annotations

from dataclasses import dataclass

from job_agent.interfaces import DraftMessage, OpenClawRuntime


@dataclass
class LocalOpenClawConfig:
    binary_path: str
    workspace_dir: str


class LocalOpenClaw(OpenClawRuntime):
    def __init__(self, config: LocalOpenClawConfig) -> None:
        self._config = config

    def start(self) -> None:
        """Start a local OpenClaw process."""
        raise NotImplementedError(
            "Wire this to the OpenClaw local binary using subprocess."
        )

    def stop(self) -> None:
        """Stop the local OpenClaw process."""
        raise NotImplementedError(
            "Wire this to the OpenClaw local binary using subprocess."
        )

    def generate_outreach(self, job_id: str) -> DraftMessage:
        """Generate a draft using the local OpenClaw runtime."""
        raise NotImplementedError(
            "Invoke OpenClaw locally to generate drafts for job_id."
        )

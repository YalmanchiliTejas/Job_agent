from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from typing import Iterable, Optional
from urllib import request

from job_agent.interfaces import DraftMessage, OpenClawRuntime


@dataclass
class LocalOpenClawConfig:
    binary_path: str
    workspace_dir: str
    server_url: Optional[str] = None
    model: str = "openclaw"
    start_command: Optional[Iterable[str]] = None
    api_key: Optional[str] = None
    timeout_s: float = 30.0

    @classmethod
    def from_env(cls) -> "LocalOpenClawConfig":
        command = os.environ.get("OPENCLAW_START_COMMAND")
        start_command = command.split() if command else None
        return cls(
            binary_path=os.environ.get("OPENCLAW_BINARY", "openclaw"),
            workspace_dir=os.environ.get("OPENCLAW_WORKSPACE", ".openclaw"),
            server_url=os.environ.get("OPENCLAW_URL"),
            model=os.environ.get("OPENCLAW_MODEL", "openclaw"),
            start_command=start_command,
            api_key=os.environ.get("OPENCLAW_API_KEY"),
        )


class LocalOpenClaw(OpenClawRuntime):
    def __init__(self, config: LocalOpenClawConfig) -> None:
        self._config = config
        self._process: Optional[subprocess.Popen[str]] = None

    def start(self) -> None:
        """Start a local OpenClaw process."""
        if self._config.start_command:
            if self._process:
                return
            self._process = subprocess.Popen(
                list(self._config.start_command),
                cwd=self._config.workspace_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            return
        if self._config.server_url:
            return
        raise RuntimeError("Set OPENCLAW_URL or OPENCLAW_START_COMMAND to start OpenClaw.")

    def stop(self) -> None:
        """Stop the local OpenClaw process."""
        if not self._process:
            return
        self._process.terminate()
        self._process.wait(timeout=10)
        self._process = None

    def generate_outreach(self, job_id: str) -> DraftMessage:
        """Generate a draft using the local OpenClaw runtime."""
        if not self._config.server_url:
            raise RuntimeError("OPENCLAW_URL must be set to generate drafts.")
        payload = {
            "model": self._config.model,
            "messages": [
                {
                    "role": "system",
                    "content": "Draft a professional outreach message for a job application.",
                },
                {"role": "user", "content": f"Create outreach for job id: {job_id}."},
            ],
        }
        req = request.Request(
            f"{self._config.server_url.rstrip('/')}/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._build_headers(),
            method="POST",
        )
        with request.urlopen(req, timeout=self._config.timeout_s) as response:
            data = json.loads(response.read().decode("utf-8"))
        content = (
            data.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "Draft unavailable.")
        )
        return DraftMessage(subject=f"Outreach for {job_id}", body=content)

    def _build_headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._config.api_key:
            headers["Authorization"] = f"Bearer {self._config.api_key}"
        return headers

from __future__ import annotations

import argparse
import os
from pathlib import Path

from job_agent.interfaces import DraftMessage, JobLink
from job_agent.openclaw_local import LocalOpenClaw, LocalOpenClawConfig
from job_agent.review import LocalReviewQueue
from job_agent.storage import JsonJobRepository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local job application agent.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(".job_agent"),
        help="Directory for local JSON storage and drafts.",
    )
    parser.add_argument(
        "--mode",
        choices=("design", "add-link", "list-pending", "approve", "generate-draft"),
        default="design",
        help="Run the basic design walkthrough.",
    )
    parser.add_argument("--url", help="Job link URL for add-link mode.")
    parser.add_argument("--source", default="manual", help="Source label for add-link mode.")
    parser.add_argument("--job-id", help="Job ID for approve mode.")
    parser.add_argument(
        "--openclaw-url",
        default=os.environ.get("OPENCLAW_URL"),
        help="Local OpenClaw server URL (or set OPENCLAW_URL).",
    )
    return parser.parse_args()


def render_design_notes() -> DraftMessage:
    return DraftMessage(
        subject="Local OpenClaw design",
        body=(
            "This CLI is a placeholder. Use README.md for the implementation steps.\n"
            "Next step: wire job_agent.openclaw_local.LocalOpenClaw to the local binary."
        ),
    )


def main() -> None:
    args = parse_args()
    repo = JsonJobRepository(args.data_dir / "jobs.json")
    review_queue = LocalReviewQueue(args.data_dir / "drafts", repo)
    if args.mode == "design":
        notes = render_design_notes()
        print(notes.subject)
        print(notes.body)
        return
    if args.mode == "add-link":
        if not args.url:
            raise SystemExit("--url is required for add-link mode.")
        job_id = repo.add_job_link(JobLink(url=args.url, source=args.source))
        draft = DraftMessage(
            subject=f"Draft outreach for {job_id}",
            body=f"Placeholder draft for {args.url}.",
        )
        review_queue.request_review(job_id, draft)
        print(f"Created {job_id} and stored draft for review.")
        return
    if args.mode == "list-pending":
        pending = list(repo.list_pending_jobs())
        print("\n".join(pending) if pending else "No pending jobs.")
        return
    if args.mode == "approve":
        if not args.job_id:
            raise SystemExit("--job-id is required for approve mode.")
        repo.mark_approved(args.job_id)
        print(f"Approved {args.job_id}.")
        return
    if args.mode == "generate-draft":
        if not args.job_id:
            raise SystemExit("--job-id is required for generate-draft mode.")
        config = LocalOpenClawConfig.from_env()
        if args.openclaw_url:
            config.server_url = args.openclaw_url
        runtime = LocalOpenClaw(config)
        runtime.start()
        try:
            job_link = repo.get_job_link(args.job_id)
            draft = runtime.generate_outreach(args.job_id)
            review_queue.request_review(
                args.job_id,
                DraftMessage(
                    subject=draft.subject,
                    body=f"{draft.body}\n\nJob link: {job_link.url}",
                ),
            )
            print(f"Generated draft for {args.job_id}.")
        finally:
            runtime.stop()
        return


if __name__ == "__main__":
    main()

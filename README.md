# Job Agent

This repository bootstraps a job-application agent that runs OpenClaw locally and exposes
a small interface for expanding into email ingestion, connection discovery, and automated
application flows.

## Quick start (design walkthrough)

```bash
python -m job_agent --mode design
```

This prints placeholder guidance while you wire in the local OpenClaw runtime.

### Local CLI (prototype)
The CLI provides a minimal loop to store job links and approvals before wiring OpenClaw:

```bash
python -m job_agent --mode add-link --url "https://example.com/job"
python -m job_agent --mode list-pending
python -m job_agent --mode approve --job-id job-1
```

To generate a draft with a local OpenClaw server running on your machine:

```bash
export OPENCLAW_URL="http://localhost:8000"
python -m job_agent --mode generate-draft --job-id job-1
```

## Local OpenClaw design (initial phase)

### 1) Run OpenClaw locally
- Install OpenClaw locally using the instructions in https://github.com/openclaw/openclaw.
- Note the local binary path and workspace directory.
- These values map to `LocalOpenClawConfig` in `job_agent/openclaw_local.py`.

### 2) Define the agent interfaces
The local-first design uses lightweight protocol interfaces so each part can be swapped later:
- `JobRepository`: stores job links and application state.
- `ReviewQueue`: holds drafts for human approval.
- `OpenClawRuntime`: the local OpenClaw connector.

See `job_agent/interfaces.py` for the initial contract definitions.

### 3) Implement the local OpenClaw runtime
Start by wiring a subprocess wrapper in `LocalOpenClaw.start()` and `.generate_outreach()`.
The goal is to avoid a hosted OpenClaw deployment and keep everything running on your machine.

`job_agent/openclaw_local.py` now includes:
- `LocalOpenClawConfig.from_env()` for environment-based configuration.
- A subprocess starter (optional) via `OPENCLAW_START_COMMAND`.
- An OpenAI-compatible HTTP request to `/v1/chat/completions` (configure with `OPENCLAW_URL`).

### 4) Add the first storage layer
`job_agent/storage.py` ships a JSON-backed repository to track job postings and approvals.
Swap it for SQLite later if you need indexing or richer queries.

### 5) Add the human review step
`job_agent/review.py` writes drafts to disk so you can approve them manually before submission.
The review queue checks approvals in the JSON repository.

## Next expansions (after local phase)
- Email ingestion to detect inbound job leads.
- Connection discovery using your inbox and LinkedIn contacts.
- Auto-draft connection emails and cover letters.
- WhatsApp ingestion to auto-create job entries from shared links.

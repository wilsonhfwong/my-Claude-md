# Add Quarterly Earnings Summarizer

## Why

Equity analysts following US-listed companies must read four distinct artifacts per
ticker per quarter — the 8-K earnings press release, the 10-Q/10-K filing, the
management slide deck, and the earnings call audio — to form a directional view.
Each artifact arrives at a different time, in a different format, and the live
earnings call (the densest qualitative signal) is audio-only and ~60 minutes long.
At a 30-name coverage list, the per-quarter time cost is unsustainable on
earnings-heavy weeks.

The current repository contains only documentation about CLAUDE.md best practices;
there is no application code. This change introduces the application from scratch
on branch `claude/financial-summary-app-WObnS`.

## What Changes

- **NEW** capability `ingestion` — fetch 8-K, 10-Q, 10-K from SEC EDGAR and
  earnings audio + IR deck from a Quartr-style paid API; user upload fallback.
- **NEW** capability `transcription` — batch STT of earnings audio in Phase 1;
  streaming STT in Phase 2.
- **NEW** capability `summarization` — produce a five-section structured summary
  (metrics, narrative, guidance & Q&A, sentiment, signal) from the ingested
  artifacts.
- **NEW** capability `signal` — emit a bullish/neutral/bearish directional signal
  with cited evidence and a non-removable informational disclaimer.
- **NEW** capability `llm-router` — provider-agnostic LLM access (Anthropic,
  OpenAI, Google, Ollama) with cost and latency accounting per call.
- **NEW** capability `prompt-registry` — versioned, append-only YAML prompt files
  with a single champion-pointer file per task.
- **NEW** capability `evaluation` — three-scorer harness (deterministic,
  reference-based, LLM-as-judge) writing both JSON and Markdown reports.
- **NEW** capability `agent-loop` — autonomous prompt-improvement and model-
  benchmarking loop with explicit stop criteria and a cost cap.
- **NEW** capability `web-ui` — FastAPI + Jinja2 + HTMX surfaces for browsing
  summaries, eval reports, leaderboard, and agent history.
- **NEW** capability `storage` — SQLite + local filesystem in v1, with schema and
  adapter design that allows a Phase-2 migration to Postgres + S3 by config only.

## Impact

- Affected specs: all listed above are NEW; no existing specs change.
- Affected code: greenfield — new `/app`, `/prompts`, `/golden`, `/eval`, `/agent`
  trees. No existing code is modified.
- Affected docs: `README.md` will gain an "App" section at the bottom; existing
  CLAUDE.md best-practices docs are untouched.
- Operational: introduces external dependencies on SEC EDGAR (free, rate-limited),
  a Quartr-style audio API (paid), at least one LLM provider (paid), and Redis
  (for ARQ workers, local).

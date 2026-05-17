# Design

## Context

Five things make this design non-trivial:

1. Four disparate input modalities (HTML/JSON filings, PDFs, audio, structured
   XBRL facts) must be reconciled into one summary.
2. Numeric accuracy is non-negotiable; "close" is wrong for EPS.
3. The signal output sits adjacent to investment advice and must be informational
   only with hard guardrails.
4. Multiple LLM providers must be swappable to enable side-by-side comparison.
5. The whole pipeline must improve itself via an autonomous agent loop without
   the agent gaming its own metrics.

## Goals / Non-Goals

**Goals (v1):** complete five-section summary per ticker+quarter for US-listed
companies; single-user local deployment; agent-driven prompt and model evaluation
with statistical confidence; verifiable numeric extraction.

**Non-Goals (v1):** trade execution, multi-tenancy, personalized advice, live
streaming transcription, non-US issuers, analyst-consensus data integration.

## Decisions

### D-1: Web framework — FastAPI
Async-native fits ARQ workers and SSE for Phase 2 streaming; Pydantic schemas
double as JSON schemas for LLM output validation.

### D-2: Frontend — Jinja2 + HTMX
Server-rendered keeps the surface small and removes a JS build step; HTMX covers
the incremental UI needs for the leaderboard and report pages without an SPA.

### D-3: Background jobs — ARQ (Redis-backed)
Asyncio-native, simpler than Celery, supports retries and cron. Phase-2 streaming
STT can reuse the same broker.

### D-4: LLM abstraction — LiteLLM
Unified `completion()` across Anthropic / OpenAI / Google / Ollama; built-in cost
tracking and caching. A custom thin wrapper buys nothing for our scope.

### D-5: Eval framework — custom Python harness
Promptfoo is YAML-first but the deterministic scorer needs arbitrary Python
(parse EDGAR XBRL facts, substring-match quotes against a transcript). A custom
runner using Inspect AI primitives keeps the agent's introspection surface
plain-file and plain-JSON.

### D-6: Versioned prompts as append-only YAML
Prompt files never mutate after commit; `index.yaml` is the only mutable pointer.
This gives the agent loop a trivially auditable change history and lets a human
roll back a champion at any time.

### D-7: Storage — SQLite v1, Postgres-portable schema
UUIDv7 TEXT PKs, ISO-8601 UTC timestamps, no SQLite-only types. A `BlobStore`
Protocol abstracts local-FS vs S3. Phase 2 migration is `alembic upgrade head` +
adapter swap.

### D-8: Signal disclaimer is wrapper-injected
The LLM cannot omit the disclaimer because it is appended by the signal wrapper,
not by the prompt. The output schema requires the field; validation rejects a
summary without it.

### D-9: Judge prompt is human-only in v1
The agent loop is forbidden from modifying the judge prompt to prevent the
classic "agent games its own metric" failure mode. Revisit once we have data on
whether human-authored variants saturate.

## Risks

| ID  | Risk                                            | Mitigation                                                                                                                  |
| --- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| R-1 | Signal interpreted as investment advice.        | Hard-coded disclaimer; ToS; informational framing; no position-size or timing recommendations.                              |
| R-2 | LLM hallucinates numbers.                       | Deterministic scorer is a gate, not a metric — summaries failing exact-match are flagged in UI and excluded from leaderboard. |
| R-3 | Agent gaming the judge.                         | Judge prompt is human-only; deterministic scorer is independent of LLMs.                                                    |
| R-4 | Runaway cost in agent loop.                     | Hard cumulative budget; per-iteration cost log; daemon refuses to start when projected spend exceeds cap.                   |
| R-5 | SEC EDGAR throttling.                           | 8 req/s token bucket; descriptive User-Agent; exponential backoff on 429.                                                   |
| R-6 | Quartr coverage gaps or ToS issues.             | Manual deck upload fallback; do not redistribute raw audio; ToS link in `docs/vendors.md`.                                  |

## Migration Plan

This is an additive change against an empty app codebase; no migration of
existing data or code is required.

## Open Questions

- **OQ-1** Which paid audio API exactly — Quartr, AlphaSense, or a different
  vendor? Pricing and ToS need to be confirmed before implementation.
- **OQ-2** Should the agent loop ever be allowed to modify the judge prompt
  (risk: gaming the metric)? Default in v1: no.
- **OQ-3** How are gold-summary references curated — by hand, by a one-time
  strongest-model run + human review, or by an external benchmark set? Default:
  one strong-model pass + human review for the 10 v1 quarters.
- **OQ-4** Authentication mechanism for Phase 2 — defer.

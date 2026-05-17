# Tasks

## 1. Project scaffolding
- [x] 1.1 Create `pyproject.toml` with Python 3.12, FastAPI, SQLAlchemy 2.0,
      Alembic, ARQ, LiteLLM, PyMuPDF, edgartools, faster-whisper, pytest, ruff.
- [x] 1.2 Create directory tree `/app`, `/prompts`, `/golden`, `/eval`, `/agent`,
      `/tests`, `/data` (gitignored).
- [x] 1.3 Add `Makefile` targets: `dev`, `worker`, `eval`, `agent`, `test`, `lint`.
- [x] 1.4 Add `docker-compose.yml` with Redis and (optional) Postgres services.
- [x] 1.5 Configure `pydantic-settings` for `.env`; secret-redaction logging filter.

## 2. Storage (capability: storage)
- [ ] 2.1 SQLAlchemy 2.0 models for: companies, quarters, filings, transcripts,
      summaries, metrics, prompts, eval_runs, eval_scores, model_leaderboard,
      agent_iterations.
- [ ] 2.2 Alembic baseline migration; verify `upgrade head` on SQLite and
      Postgres container.
- [ ] 2.3 Blob storage adapter: `LocalBlobStore` (v1) and `S3BlobStore` (stub,
      Phase 2) behind a `BlobStore` Protocol.

## 3. Ingestion (capability: ingestion)
- [ ] 3.1 EDGAR client using `edgartools`; descriptive User-Agent; token-bucket
      limiter at 8 req/s; idempotent fetch keyed on (ticker, period, kind).
- [ ] 3.2 Quartr-style audio + deck client behind an `EarningsAudioProvider`
      Protocol; record SHA-256 of every blob.
- [ ] 3.3 Manual deck upload endpoint with PyMuPDF metadata scrubbing.

## 4. Transcription (capability: transcription)
- [ ] 4.1 Batch STT worker using `faster-whisper`; outputs time-coded segments.
- [ ] 4.2 WER spot-check tool: sample 10 × 30-second clips, compare against the
      Quartr transcript, fail the build if WER > 8% on the AAPL anchor case.
- [ ] 4.3 [Phase 2] Deepgram streaming STT worker + SSE channel.

## 5. LLM router (capability: llm-router)
- [ ] 5.1 LiteLLM wrapper exposing `complete(prompt_id, inputs, model) ->
      Completion` with `tokens_in`, `tokens_out`, `cost_usd`, `latency_ms`.
- [ ] 5.2 Cost accounting persisted on every call; redact prompt body at default
      log level.

## 6. Prompt registry (capability: prompt-registry)
- [ ] 6.1 Loader for `prompts/<task>/<name>.v<N>.yaml` and `index.yaml`.
- [ ] 6.2 Syntactic linter; CI fails on unknown fields or missing schema link.
- [ ] 6.3 Seed champion prompts v1 for tasks: `metrics`, `narrative`, `guidance`,
      `sentiment`, `signal`, `judge`.

## 7. Summarization (capability: summarization)
- [ ] 7.1 Per-section summarizer modules consuming structured inputs (filings,
      transcript, deck text).
- [ ] 7.2 JSON output schemas under `app/summarize/schemas/`; validate every
      output against schema; reject and retry on validation failure.
- [ ] 7.3 Citation enforcement: every quoted line in `guidance_qa` must be a
      substring of the transcript (normalized whitespace).

## 8. Signal (capability: signal)
- [ ] 8.1 Signal classifier emitting `{bullish, neutral, bearish}` + confidence
      in [0, 1] + evidence[] with artifact pointers.
- [ ] 8.2 Disclaimer field is hard-coded and cannot be omitted by the LLM (added
      by the wrapper, not by the prompt).

## 9. Evaluation (capability: evaluation)
- [ ] 9.1 Gold-set scaffolding under `/golden/<set>/manifest.yaml`; seed 10
      quarters including AAPL FY2025 Q2.
- [ ] 9.2 Deterministic scorer: EPS exact-cent match; revenue within $0.5M.
- [ ] 9.3 Reference scorer: embedding cosine + ROUGE-L per section.
- [ ] 9.4 Judge scorer: separate versioned judge prompt + 1-5 Likert rubric.
- [ ] 9.5 `eval/run.py` aggregates with 95% bootstrap CIs and writes
      `reports/<run_id>.json` and `reports/<run_id>.md`.

## 10. Agent loop (capability: agent-loop)
- [ ] 10.1 `agent/loop.py` using the Anthropic Agent SDK; one iteration per
      invocation.
- [ ] 10.2 Stop criteria in `agent/policies.py`: plateau-5, max-50/week, cost cap
      $50/run, judge threshold met.
- [ ] 10.3 Every accepted/rejected variant recorded in `agent_iterations`.

## 11. Web UI (capability: web-ui)
- [ ] 11.1 Routers and Jinja templates: company list, company detail, summary
      detail, eval report, leaderboard, agent history.
- [ ] 11.2 Disclaimer is rendered on every page that displays a signal.

## 12. Verification
- [ ] 12.1 End-to-end run on AAPL FY2025 Q2 produces a summary whose metrics
      pass the deterministic scorer for Claude Sonnet 4.6, GPT-4 (4.1), and
      Gemini 2.5 Pro.
- [ ] 12.2 One full agent-loop iteration on an intentionally-vague v0 prompt
      proposes v1, evaluates, and decides accept/reject with a written rationale.
- [ ] 12.3 `alembic upgrade head` on a Postgres container produces a working
      schema; the same eval run yields byte-identical report JSON.

## 13. Phase 2 (out of scope for this change; tracked separately)
- [ ] 13.1 Streaming STT.
- [ ] 13.2 Analyst-consensus ingestion (IBES/Zacks).
- [ ] 13.3 Postgres + S3 migration.
- [ ] 13.4 Multi-user auth, watchlists, alerts.

# Project: MegaCorp Platform

Enterprise SaaS platform. Go backend (microservices), React frontend, PostgreSQL + Redis.
Monorepo with Bazel build system. Kubernetes deployment.

## Commands
- Build all: `bazel build //...`
- Build service: `bazel build //services/<name>/...`
- Test all: `bazel test //...`
- Test service: `bazel test //services/<name>/...`
- Lint: `make lint` (golangci-lint + eslint)
- Generate protos: `make proto`
- Local dev: `make dev` (starts docker-compose stack)
- DB migrate: `make migrate-up`

## Architecture
- `services/` -- Go microservices (one per directory)
- `frontend/` -- React SPA (Next.js)
- `proto/` -- Protobuf definitions (source of truth for API contracts)
- `pkg/` -- Shared Go packages
- `deploy/` -- Kubernetes manifests and Helm charts

## Behavioral Rules

### Honesty and Verification
- If unsure whether a function, package, or API exists in this codebase, grep for it first. Do not invent interfaces.
- Before modifying any file, read it first. Understand the existing implementation.
- When fixing a bug, write a failing test first (`bazel test //services/<name>/...`), then fix it.
- Run `bazel test //services/<name>/...` after changes. Do not consider a task done until tests pass.

### Scope Control
- Do not add features, refactors, or "improvements" beyond what was asked.
- Do not add new Go dependencies without listing them and asking first.
- Keep diffs small. One goal per change. Do not refactor surrounding code.
- Functions ≤40 lines. If longer, extract helpers.

### Communication
- If critical information is missing, ask instead of guessing.
- When encountering a choice between approaches, briefly explain both and ask which to use.

## Project-Specific Rules

### Critical
- **CRITICAL**: All API changes start with proto definitions in `proto/`. Generate code with `make proto`. Never hand-write protobuf-generated code.
- **CRITICAL**: No secrets in code. Use `pkg/config` to read from environment.
- **IMPORTANT**: All database migrations are forward-only. Never modify existing migration files.

### Go Conventions
- Error handling: wrap errors with `fmt.Errorf("context: %w", err)`. Never swallow errors silently.
- Logging: use `pkg/log` (structured logger). Never use `fmt.Println` or `log.Printf` in services.
- Feature flags: check `pkg/flags` before implementing conditional behavior.

### Domain-Specific Rules
- See `.claude/rules/code-style.md` for frontend conventions.
- See `.claude/rules/testing.md` for test requirements.
- See `.claude/rules/deployment.md` for deployment procedures.

- **IMPORTANT**: Never push directly to `main` or `release/*` branches.

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
- `tools/` -- Build and deployment tooling
- `deploy/` -- Kubernetes manifests and Helm charts

## Rules

### Critical
- **CRITICAL**: All API changes start with proto definitions in `proto/`. Generate code with `make proto`. Never hand-write protobuf-generated code.
- **CRITICAL**: No secrets in code. Use `pkg/config` to read from environment. Never hardcode connection strings, API keys, or credentials.
- **IMPORTANT**: All database migrations are forward-only. Never modify existing migration files in `migrations/`.

### General
- Go code follows the project style in `pkg/style/`. Run `golangci-lint` before committing.
- Error handling: wrap errors with `fmt.Errorf("context: %w", err)`. Never swallow errors silently.
- Logging: use `pkg/log` (structured logger). Never use `fmt.Println` or `log.Printf` in services.
- Feature flags: check `pkg/flags` before implementing conditional behavior. Flag names use `snake_case`.

### Frontend
- See `.claude/rules/code-style.md` for detailed frontend conventions.

### Testing
- See `.claude/rules/testing.md` for test requirements.

### Deployment
- See `.claude/rules/deployment.md` for deployment procedures.

- **IMPORTANT**: Never push directly to `main` or `release/*` branches. All changes go through PRs with required reviewers.

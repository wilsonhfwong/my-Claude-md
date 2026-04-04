# Project: Acme Dashboard

React 18 + TypeScript frontend with Express + Prisma backend.
Monorepo managed with Turborepo.

## Commands
- Install: `pnpm install` (from root)
- Dev: `pnpm dev` (starts both frontend and backend)
- Build: `pnpm build`
- Test: `pnpm test` (vitest for frontend, jest for backend)
- Test single: `pnpm test -- path/to/file.test.ts`
- Lint: `pnpm lint` (eslint + prettier)
- Type check: `pnpm tsc --noEmit`
- DB migrate: `pnpm --filter backend prisma migrate dev`

## Architecture
- `apps/frontend/` -- React SPA (Vite)
- `apps/backend/` -- Express API server
- `packages/shared/` -- Shared types and utilities
- `packages/ui/` -- Shared React component library

## Behavioral Rules

### Honesty and Verification
- If unsure whether a function, API, or library method exists, search the codebase or docs first. Do not invent interfaces.
- Before modifying any file, read it first. Understand existing code before making changes.
- If critical information is missing, ask me instead of guessing.

### Scope Control
- Do not add features, refactors, or "improvements" beyond what was asked.
- Do not add new packages without listing them and asking first.
- Keep diffs small. One goal per change.

### Testing
- Run `pnpm test` after changes. Do not consider a task done until tests pass.
- When fixing a bug, write a failing test first, then fix it.
- Do not modify existing test assertions unless I specifically ask.

## Project-Specific Rules

### General
- Use `pnpm`, not `npm` or `yarn`. Lockfile: pnpm-lock.yaml.
- Import shared types from `@acme/shared`. Never duplicate type definitions.
- All dates use `date-fns`. No `moment.js`, no raw Date manipulation.

### Backend
- API responses use `{ data, error, meta }` envelope from `packages/shared/src/api.ts`.
- Throw `AppError` from `apps/backend/src/errors.ts`, never raw `Error`.
- Database access through repos in `apps/backend/src/repos/`. No direct Prisma in handlers.

### Frontend
- Components use `ComponentName/` directory pattern: `index.tsx`, `ComponentName.test.tsx`.
- State: Zustand stores in `apps/frontend/src/stores/`. No prop drilling past 2 levels.
- API calls through hooks in `apps/frontend/src/hooks/api/`. No direct `fetch` in components.

<important if="modifying database schema">
Always create a migration: `pnpm --filter backend prisma migrate dev --name describe_change`.
Never modify existing migrations. Migrations are forward-only.
Run `pnpm --filter backend prisma generate` after schema changes.
</important>

<important if="creating new API endpoints">
1. Define Zod schema in `apps/backend/src/schemas/`.
2. Create handler in `apps/backend/src/handlers/`.
3. Register route in `apps/backend/src/routes/index.ts`.
4. Add API hook in `apps/frontend/src/hooks/api/`.
</important>

- **CRITICAL**: Never commit `.env` files. They contain production secrets.
- **IMPORTANT**: Never push directly to `main`. Always create a feature branch.

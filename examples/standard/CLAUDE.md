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

## Project Structure
- `apps/frontend/` -- React SPA (Vite)
- `apps/backend/` -- Express API server
- `packages/shared/` -- Shared types and utilities
- `packages/ui/` -- Shared React component library

## Rules

### General
- Use `pnpm`, not `npm` or `yarn`. Lockfile: pnpm-lock.yaml.
- Import shared types from `@acme/shared`, never duplicate type definitions.
- All dates use `date-fns`. No `moment.js`, no raw Date manipulation.

### Backend
- API responses use `{ data, error, meta }` envelope from `packages/shared/src/api.ts`.
- Throw `AppError` from `apps/backend/src/errors.ts`, never raw `Error`.
- Database access through repos in `apps/backend/src/repos/`. No direct Prisma in handlers.
- New routes register in `apps/backend/src/routes/index.ts`.

### Frontend
- Components in `apps/frontend/src/components/` use the `ComponentName/` directory pattern:
  `ComponentName/index.tsx`, `ComponentName/ComponentName.test.tsx`, `ComponentName/styles.ts`.
- State management: Zustand stores in `apps/frontend/src/stores/`. No prop drilling past 2 levels.
- API calls go through hooks in `apps/frontend/src/hooks/api/`. No direct `fetch` in components.

### Testing
- Backend tests mock the database with `prismock`.
- Frontend tests use `@testing-library/react`. No `enzyme`.
- Each test file: at least one happy path + one error case.

<important if="modifying database schema">
Always create a migration: `pnpm --filter backend prisma migrate dev --name describe_change`.
Never modify existing migrations. Create new ones.
Run `pnpm --filter backend prisma generate` after schema changes.
</important>

<important if="creating new API endpoints">
1. Define Zod schema in `apps/backend/src/schemas/`.
2. Create handler in `apps/backend/src/handlers/`.
3. Register route in `apps/backend/src/routes/index.ts`.
4. Add corresponding API hook in `apps/frontend/src/hooks/api/`.
</important>

- **CRITICAL**: Never commit `.env` files. They contain production secrets.
- **IMPORTANT**: Never push directly to `main`. Always create a feature branch.

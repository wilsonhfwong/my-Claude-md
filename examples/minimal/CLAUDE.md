# Project: url-shortener

Node.js CLI tool. TypeScript + tsx for execution.

## Commands
- Run: `npx tsx src/index.ts`
- Test: `npm test` (jest)
- Build: `npm run build` (tsc)

## Rules

### Behavior
- If unsure whether a function or library method exists, search the codebase first. Do not invent interfaces.
- Before modifying any file, read it first.
- Do not add features or refactors beyond what was asked.
- Run `npm test` after changes. Do not consider a task done until tests pass.
- If critical information is missing, ask me instead of guessing.

### Project-Specific
- Use `npm`, not `yarn`. Lockfile: package-lock.json.
- All URLs validated with the `URL` constructor before storage.
- Short codes are 6 characters, base62 encoded. See src/encoding.ts.
- Tests go in `__tests__/`, mirroring src/ structure.
- **CRITICAL**: Never log or expose DATABASE_URL. It contains credentials.

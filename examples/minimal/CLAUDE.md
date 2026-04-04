# Project: url-shortener

Node.js CLI tool. TypeScript + tsx for execution.

## Commands
- Run: `npx tsx src/index.ts`
- Test: `npm test` (jest)
- Build: `npm run build` (tsc)

## Rules
- Use `npm`, not `yarn`. Lockfile: package-lock.json.
- All URLs are validated with the `URL` constructor before storage.
- Short codes are 6 characters, base62 encoded. See src/encoding.ts.
- Tests go in `__tests__/` directory, mirroring src/ structure.
- **CRITICAL**: Never log or expose the DATABASE_URL. It contains credentials.

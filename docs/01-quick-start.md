# Quick Start: Your First CLAUDE.md in 5 Minutes

## What Is CLAUDE.md?

CLAUDE.md is a file you place in the root of your project that gives Claude Code persistent instructions. Think of it as a briefing document -- it tells Claude how your project works, what conventions to follow, and what mistakes to avoid.

Without it, Claude relies on general knowledge. With it, Claude works like a teammate who already knows your codebase.

## Where Does It Go?

Create a file called `CLAUDE.md` in your project root (the same directory as your `package.json`, `Cargo.toml`, or equivalent).

```
my-project/
  CLAUDE.md    <-- here
  src/
  package.json
```

## The "5 Rules" Approach

Don't write a novel. Start with **5 rules** based on the mistakes you correct most often. Here's the thought process:

1. Think of the last 5 times you corrected Claude (or any AI assistant)
2. Write one rule for each correction
3. That's your CLAUDE.md

## A Complete Example (~20 lines)

```markdown
# Project: Acme API

TypeScript + Express backend. PostgreSQL database via Prisma ORM.

## Commands
- Build: `pnpm build`
- Test: `pnpm test` (runs vitest)
- Lint: `pnpm lint` (runs eslint + prettier)

## Rules
- Use `pnpm`, not `npm` or `yarn`. The lockfile is pnpm-lock.yaml.
- All API responses use the `{ data, error, meta }` envelope format defined in src/types/api.ts.
- Database migrations go in prisma/migrations/. Never modify the database schema directly.
- Error handling: throw AppError (from src/errors.ts), never raw Error.
- Tests live next to source files as `*.test.ts`, not in a separate test/ directory.
```

That's it. 20 lines. This outperforms a 500-line CLAUDE.md because every line prevents a real mistake.

## What NOT to Put in Your First Version

- **Style guides** -- let your linter handle formatting (use Hooks for enforcement)
- **Architecture documentation** -- that belongs in your README or docs/
- **Generic guidelines** -- "write clean code" is meaningless; be specific
- **Everything you know** -- add rules incrementally as problems surface

## The Question Test

Before adding any rule, ask: **"Would Claude make a mistake without this?"**

- If Claude already does it correctly -> don't add it
- If it's a style preference -> use a linter/formatter Hook instead
- If it's a real, repeated mistake -> add it

## Generating a Starter

You can also run `/init` in Claude Code to auto-generate a starter CLAUDE.md from your project. But then **delete half of what it generates** -- auto-generated files tend to be bloated.

## Next Steps

- [Hierarchy and Precedence](02-hierarchy-and-precedence.md) -- learn about user-level vs project-level CLAUDE.md
- [Writing Effective Rules](04-writing-effective-rules.md) -- techniques for rules that Claude actually follows

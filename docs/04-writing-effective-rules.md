# Writing Effective Rules

The difference between a CLAUDE.md that works and one that doesn't comes down to how rules are written. This guide covers the core techniques.

## The Question Test

Before adding any rule, ask: **"Would Claude make a mistake without this?"**

- **Yes, repeatedly** -> Add it. This is what CLAUDE.md is for.
- **Yes, but rarely** -> Consider adding it. Monitor if it helps.
- **No, Claude does this anyway** -> Don't add it. You're wasting an instruction slot.
- **It's a style preference** -> Use a linter/formatter Hook instead (100% compliance, zero instruction cost).

This single filter eliminates most CLAUDE.md bloat.

## The WHAT-WHY-HOW Framework

Each rule should communicate three things:

1. **WHAT** to do (the instruction)
2. **WHY** it matters (briefly -- one clause is enough)
3. **HOW** to do it (if non-obvious)

### Example

```markdown
Use `pnpm`, not `npm` or `yarn` (the lockfile is pnpm-lock.yaml).
Run `pnpm install` before suggesting dependency changes.
```

- WHAT: Use pnpm
- WHY: the lockfile is pnpm-lock.yaml (implies: using npm would create a second lockfile)
- HOW: `pnpm install` (the specific command)

### Anti-Pattern

```markdown
Please use pnpm for all package management operations.
```

Missing the WHY (Claude doesn't know why this matters) and the HOW (what if Claude needs to install something?).

## Size Targets

| Size | Assessment |
|------|-----------|
| 15-40 lines | Excellent. Focused and effective. |
| 40-80 lines | Ideal sweet spot for most projects. |
| 80-200 lines | Acceptable for complex projects. Review for bloat. |
| 200-500 lines | Diminishing returns. Actively prune. |
| 500+ lines | Harmful. Compliance degrades significantly. |

**Rule of thumb**: Start with 5 rules. Add one per week as problems surface. Prune monthly.

## One Rule, One Line

Prefer single-sentence rules. If a rule needs a paragraph, it's probably two rules -- or it belongs in documentation, not CLAUDE.md.

### Good
```markdown
- Functions must be under 40 lines. Extract helpers if longer.
- All API endpoints return the `{ data, error, meta }` envelope from src/types/api.ts.
- Never use `any` type. Use `unknown` and narrow with type guards.
```

### Bad
```markdown
- When writing functions, try to keep them reasonably short. As a general guideline,
  functions should ideally be under 40 lines, though there may be exceptions. If a
  function is getting long, consider whether parts of it could be extracted into
  helper functions that have clear names describing what they do.
```

The "bad" version uses 4 lines to say what the "good" version says in 1. It also hedges ("try to", "ideally", "though there may be exceptions") which gives Claude permission to ignore it.

## Be Specific, Not Aspirational

Rules must be **actionable and verifiable**. Claude can follow "functions under 40 lines" because it can count. It cannot follow "write clean code" because that's subjective.

### Specific (Works)
```markdown
- Error handling: throw `AppError` from src/errors.ts, never raw `Error`.
- Database queries use the repository pattern in src/repos/. No direct Prisma calls in route handlers.
- Commit messages follow Conventional Commits: `type(scope): description`.
```

### Vague (Doesn't Work)
```markdown
- Follow best practices for error handling.
- Use proper architectural patterns for database access.
- Write meaningful commit messages.
```

## Use Conditional Blocks

Wrap task-specific rules in conditional blocks so they only activate when relevant:

```markdown
<important if="writing or modifying tests">
- Tests use `describe`/`it` blocks, not `test()`.
- Mock external services with `vi.mock()`, never make real HTTP calls in tests.
- Each test file must have at least one test for the happy path and one for error handling.
</important>

<important if="modifying API endpoints">
- All endpoints must validate input with Zod schemas from src/schemas/.
- Return appropriate HTTP status codes (don't default to 200 for everything).
</important>
```

**Tips for conditions**:
- Make them narrow: `if="writing tests"` is better than `if="writing code"` (everything is writing code)
- Use action verbs: `if="modifying database schema"` not `if="database"`
- Don't over-segment: if a rule applies 80%+ of the time, it doesn't need a condition

## Use Emphasis for Critical Rules

For rules that are truly non-negotiable, use emphasis:

```markdown
- **IMPORTANT**: Never commit directly to `main`. Always create a feature branch.
- **CRITICAL**: The `.env` file contains production secrets. Never read, log, or commit it.
```

Claude pays more attention to emphasized rules. But if everything is IMPORTANT, nothing is. Reserve emphasis for 2-3 rules maximum.

## Include Commands and Paths

Claude works better with concrete references than abstract descriptions.

### Good
```markdown
- Build: `pnpm build`
- Test: `pnpm test` (runs vitest)
- Lint: `pnpm lint` (eslint + prettier)
- Database types are generated from schema: `pnpm prisma generate`
- Shared types live in `src/types/`. Import from there, don't duplicate type definitions.
```

### Bad
```markdown
- Use the project's build tool to compile the code.
- Run the test suite before submitting changes.
- Make sure the code passes linting.
```

Claude doesn't know which build tool, which test command, or which linter unless you tell it.

## Negative Rules (What NOT to Do)

"Don't do X" rules are effective when they prevent common mistakes:

```markdown
- Never use `console.log` for debugging in production code. Use the logger from src/lib/logger.ts.
- Don't create new files in src/utils/. Add functions to existing domain-specific modules.
- Don't use `any` type. If the type is truly unknown, use `unknown` with type guards.
```

Negative rules work best when:
- Claude has made the mistake before (or commonly makes it in similar projects)
- The correct alternative is stated clearly
- The rule is specific enough to be actionable

## Before and After: A Complete Rewrite

### Before (Bloated, ~40 lines of low value)
```markdown
# Development Guidelines

## General Principles
- Write clean, maintainable code
- Follow SOLID principles
- Use meaningful variable names
- Keep functions small and focused
- Write comprehensive tests
- Document your code appropriately
- Handle errors gracefully
- Use TypeScript features effectively
- Follow the existing code style
- Keep dependencies up to date
...
```

### After (Focused, ~15 lines of high value)
```markdown
# Acme API

TypeScript + Express + Prisma. Run with `pnpm`.

## Commands
- Build: `pnpm build` | Test: `pnpm test` | Lint: `pnpm lint`

## Rules
- Use `pnpm`, not `npm`. Lockfile: pnpm-lock.yaml.
- API responses use `{ data, error, meta }` envelope (src/types/api.ts).
- Throw `AppError` (src/errors.ts), not raw `Error`.
- Tests live next to source: `*.test.ts`. Use `vi.mock()` for externals.
- Database access through repos in src/repos/. No direct Prisma in handlers.
- Never use `any`. Use `unknown` with type guards.
- **CRITICAL**: Never commit .env files. They contain production secrets.
```

Every line in the "After" version prevents a real mistake. The "Before" version is aspirational noise.

## Next Steps

- [CLAUDE.md vs Settings vs Hooks](05-claude-md-vs-settings-vs-hooks.md) -- know when rules belong elsewhere
- [What Works and What Doesn't](06-what-works-and-what-doesnt.md) -- empirical findings from the community

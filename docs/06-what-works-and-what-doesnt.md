# What Works and What Doesn't

Empirical findings from the community -- what actually improves Claude Code's output and what wastes your time.

## What Works

### 1. Ruthless Pruning

The single most effective technique. For every rule, apply the [Question Test](04-writing-effective-rules.md): "Would Claude make a mistake without this?"

Community reports consistently show that a pruned 30-line CLAUDE.md outperforms an unpruned 300-line one. The instruction budget is finite. Every weak rule dilutes the strong ones.

### 2. Addressing Repeated Pain Points

The best rules come from real mistakes. If you've corrected Claude 3+ times on the same issue, that's a CLAUDE.md rule. If you've never seen Claude make a particular mistake, don't preemptively add a rule for it.

**Process**: Work with Claude for a week without CLAUDE.md. Note every correction. Those corrections become your rules.

### 3. Concrete Over Abstract

Rules with specific file paths, command names, and exact patterns consistently outperform abstract guidelines.

| Abstract (Low Compliance) | Concrete (High Compliance) |
|---------------------------|---------------------------|
| "Use proper error handling" | "Throw `AppError` from `src/errors.ts`" |
| "Follow the project structure" | "New API routes go in `src/routes/`" |
| "Run tests before committing" | "Run `pnpm test` -- all tests must pass" |

### 4. Hooks for Absolutes

Rules with the word "never" or "always" belong in Hooks, not just CLAUDE.md. CLAUDE.md compliance is ~70%. Hooks are 100%.

Community pattern: Put the rule in both CLAUDE.md (so Claude understands why) and a Hook (so it's enforced).

### 5. Starting Small and Growing Incrementally

Projects that start with 5 rules and add one per week produce better CLAUDE.md files than projects that try to write everything upfront.

Starting small forces you to prioritize. Adding incrementally means every rule addresses a real problem.

### 6. Monthly Review Cycles

Teams that review CLAUDE.md monthly and delete stale rules maintain higher compliance than teams that treat it as a write-once file.

Review question: "Did this rule prevent a mistake in the last 30 days?" If not, delete it.

### 7. Including Build/Test/Lint Commands

One of the highest-value-per-line additions. Claude frequently needs to run commands, and guessing wrong wastes time:

```markdown
## Commands
- Build: `pnpm build`
- Test: `pnpm test` (vitest, runs in watch mode)
- Test single file: `pnpm test -- path/to/file.test.ts`
- Lint: `pnpm lint`
- Type check: `pnpm tsc --noEmit`
```

### 8. Explaining Architectural Decisions

Not architecture documentation -- just the decisions that affect how Claude should write code:

```markdown
- We use the repository pattern: data access in src/repos/, business logic in src/services/.
  Route handlers call services, never repos directly.
- Feature flags are in src/flags.ts. Check flags before implementing conditional behavior.
```

## What Doesn't Work

### 1. The Dumping Ground

Treating CLAUDE.md as a place to put "everything Claude should know." This creates a 500+ line file where nothing gets enough attention.

**Symptom**: Your CLAUDE.md is longer than your README.
**Fix**: Apply the Question Test. Move documentation to docs/. Move style rules to Hooks.

### 2. Treating It Like Documentation

CLAUDE.md is instructions, not onboarding docs. Claude doesn't need your project's history, design philosophy, or team structure.

**Symptom**: Paragraphs of prose explaining why decisions were made.
**Fix**: One sentence per rule. If you need to explain context, one parenthetical clause is enough.

### 3. Code Style Rules

Formatting rules (indentation, semicolons, quotes, trailing commas) are better handled by linters and formatters via Hooks. They get 100% compliance at zero instruction cost.

**Symptom**: "Use 2-space indentation", "Always use semicolons", "Prefer single quotes".
**Fix**: Set up Prettier/ESLint as a PostToolUse Hook.

### 4. Generic Guidelines

Claude already knows general software engineering principles. Telling it to "write clean code" or "follow SOLID" wastes an instruction slot on something it already does.

**Symptom**: Rules that could apply to any project in any language.
**Fix**: Delete them. Only add project-specific rules.

### 5. Auto-Generated CLAUDE.md Without Editing

Running `/init` and committing the result without editing produces a bloated, generic file. Auto-generation is a starting point, not an end product.

**Symptom**: The CLAUDE.md reads like a project summary, not a set of instructions.
**Fix**: After `/init`, delete at least half the content. Keep only what passes the Question Test.

### 6. Files Over 500 Lines

Community testing shows compliance drops significantly past 500 lines. At 1000+ lines, Claude may effectively ignore entire sections during context compression.

**Symptom**: You notice Claude not following rules that are clearly in your CLAUDE.md.
**Fix**: Aggressively prune. Move task-specific rules to `.claude/rules/*.md`. Move style to Hooks.

### 7. Contradictory Rules

When rules conflict, Claude picks one unpredictably. Worse, the contradiction may cause it to partially follow both, producing inconsistent output.

**Symptom**: Claude sometimes does X and sometimes does Y for the same situation.
**Fix**: Search your CLAUDE.md for contradictions. Clarify which rule applies when.

### 8. Duplicating README Content

If your README already explains the project structure, don't repeat it in CLAUDE.md. Claude reads other files too. CLAUDE.md is for instructions, not information that exists elsewhere.

**Symptom**: CLAUDE.md has a "Project Overview" section that mirrors the README.
**Fix**: Delete it. If Claude needs project context, a one-line summary suffices.

## Community-Reported Compliance Rates

Based on informal community testing (not rigorous benchmarks):

| Technique | Estimated Compliance |
|-----------|---------------------|
| Hook enforcement | ~100% |
| settings.json permissions | ~100% |
| Emphasized CLAUDE.md rule (CRITICAL/IMPORTANT) | ~85-90% |
| Standard CLAUDE.md rule (well-written) | ~70-80% |
| Standard CLAUDE.md rule (vague) | ~40-60% |
| Rule buried in 500+ line file | ~30-50% |
| Generic guideline ("write clean code") | ~0% (Claude already does this) |

## The 80/20 of CLAUDE.md

If you only do five things:

1. **Add your build/test/lint commands** -- highest value per line
2. **Add 5 rules for your most common corrections** -- addresses real pain
3. **Set up a PostToolUse Hook for formatting** -- free 100% compliance
4. **Keep it under 80 lines** -- protects your instruction budget
5. **Review monthly and delete stale rules** -- prevents decay

This gets you 80% of the value with 20% of the effort.

## Next Steps

- [Advanced Techniques](07-advanced-techniques.md) -- multi-agent patterns and prompt caching
- [Maintenance Lifecycle](08-maintenance-lifecycle.md) -- how to keep your CLAUDE.md effective over time

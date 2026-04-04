# Scope Control: Preventing Over-Engineering

Claude Code's second most common failure mode: doing too much. Adding unrequested features, refactoring code you didn't ask about, installing new packages without asking, "improving" things that work fine.

## The Problem

Without scope control rules, Claude will:
- Rewrite half the file when asked to change one function
- Add error handling for scenarios that can't happen
- Create helper functions and abstractions for one-time operations
- Install new packages without checking if existing tools suffice
- Add docstrings, comments, and type annotations to unchanged code
- Refactor surrounding code while fixing a bug
- "Improve" working code to match its idea of best practices

## The Rules

### Rule 1: Keep Diffs Small

```markdown
- Keep the diff small. Only change what's needed to complete the task.
  Do not refactor or "improve" surrounding code.
```

**Source**: Builder.io, RanTheBuilder, AIMonks "8 Golden Rules"

### Rule 2: No Unrequested Features

```markdown
- Do not add features, error handling, or "improvements" beyond what was
  requested. A bug fix doesn't need surrounding code cleaned up. A simple
  feature doesn't need extra configurability.
```

Note: this exact principle is **baked into Claude Code's system prompt** (`getSimpleDoingTasksSection()`). Adding it to your CLAUDE.md reinforces it with the distributed repetition strategy that Anthropic itself uses (same instruction, different wording, different location → stronger compliance).

### Rule 3: Ask Before Adding Dependencies

```markdown
- Do not add new packages or dependencies without listing them and asking
  me first.
```

**Why**: Claude frequently pulls in packages you don't want, creating supply chain risk. This rule forces a checkpoint.

### Rule 4: One Goal Per Change

```markdown
- One goal per change. Keep diffs reviewable and rollback-safe.
```

**Source**: Nathan Onn, "CLAUDE.md: The Highest Leverage File"

### Rule 5: Don't Touch What You Didn't Change

```markdown
- Do not add docstrings, comments, or type annotations to code you
  didn't modify. Do not rename variables in code outside the scope
  of the current task.
```

This is already in Claude Code's system prompt, but reinforcing it in CLAUDE.md catches the cases where the system prompt instruction gets diluted by a long conversation.

## Project-Specific Scope Rules

These are highly effective because they address **your** specific pain points:

```markdown
- Do NOT modify auth middleware without being explicitly asked.
- Do NOT change the database schema without discussing the migration plan first.
- Do NOT modify files in src/core/ — these are stable, shared foundations.
- Do NOT modify existing test assertions. Add new tests instead.
```

The pattern: identify **which parts of your codebase are sensitive** and explicitly fence them off.

## Scope Control via File-Scoped Rules

Use `.claude/rules/` with path-scoped loading for sensitive areas:

```markdown
<!-- .claude/rules/core-protection.md -->
---
paths:
  - src/core/**
---

<important>
Files in src/core/ are stable foundations used by the entire codebase.
Do not modify these files unless the task explicitly requires it.
If a change is needed, describe the proposed change and get confirmation first.
</important>
```

This rule only loads when Claude reads files in `src/core/`, saving token budget the rest of the time.

## The "Three Lines Is Better" Principle

From Anthropic's own system prompt:

> "Three similar lines of code is better than a premature abstraction."

Claude loves to create abstractions. It sees three similar code blocks and wants to extract a shared function. Usually this makes the code worse (harder to modify independently, harder to understand, premature generalization).

Add this rule if Claude keeps abstracting:

```markdown
- Do not create helpers or utilities for one-time operations.
  Three similar lines of code is better than a premature abstraction.
```

## Sources

- Anthropic Official Best Practices — code.claude.com/docs/en/best-practices
- Anthropic System Prompt (getSimpleDoingTasksSection) — Wisely Chen analysis
- Builder.io: "50 Claude Code Tips" — builder.io/blog/claude-code-tips-best-practices
- RanTheBuilder: "Lessons From Real Projects" — ranthebuilder.cloud
- AIMonks: "8 Golden Rules" — medium.com/aimonks
- Nathan Onn: "CLAUDE.md: The Highest Leverage File" — nathanonn.com
- HumanLayer: "Writing a good CLAUDE.md" — humanlayer.dev

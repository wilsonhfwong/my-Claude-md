# Testing and Verification

Anthropic's internal teams call this "the single highest-leverage thing you can do." Community testing shows a **2-3x quality improvement** when Claude runs tests in a loop (write → test → fix → re-test).

## The Problem

Without verification rules, Claude will:
- Declare bugs "fixed" after editing code, without running the code
- Run tests, see failures, and make changes that break other tests
- Test only the changed file, missing integration-level breakage
- Mock too aggressively, making tests pass but missing real bugs
- Skip verification entirely when confident in its changes

The most damning example: [Christopher Meiklejohn's post](https://christophermeiklejohn.com/ai/claude/2026/03/08/claude-tested-everything-except-the-one-thing-that-mattered.html) — "Claude Tested Everything Except the One Thing That Mattered."

## The Rules

### Rule 1: Always Run Tests

```markdown
- Run tests after making changes. Do not consider a task complete until
  tests pass.
```

Simple, but the highest-impact single rule you can add. Even at ~70% compliance, this catches a huge number of bugs that would otherwise ship.

### Rule 2: Reproduce Before Fixing

```markdown
- When fixing a bug, write a failing test that reproduces the issue first.
  Then fix it. Then verify the test passes.
```

This prevents Claude from "fixing" bugs it doesn't actually understand. If it can't reproduce the bug in a test, it probably can't fix it reliably.

### Rule 3: Run Targeted Tests

```markdown
- Prefer running single test files over the full suite. Use:
  `pnpm test -- path/to/file.test.ts`
  Only run the full suite before committing.
```

**Why**: Running the full test suite on every change wastes tokens (Claude reads all the output) and time. Targeted tests give faster feedback.

### Rule 4: End-to-End Verification

```markdown
- Verify fixes end-to-end, not just that the changed file compiles.
  A type-checking change can break runtime behavior in another file.
```

### Rule 5: Include Build/Test/Lint Commands

The single highest value-per-line content you can add to CLAUDE.md:

```markdown
## Commands
- Build: `pnpm build`
- Test: `pnpm test` (vitest)
- Test single: `pnpm test -- path/to/file.test.ts`
- Lint: `pnpm lint`
- Type check: `pnpm tsc --noEmit`
```

Without this, Claude guesses at commands (and frequently guesses wrong).

## Verification with Hooks

For 100% compliance, gate commits on passing tests:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+commit'; then pnpm test 2>&1 || (echo 'BLOCKED: Tests must pass before committing' >&2; exit 1); fi"
    }]
  }
}
```

## LSP: The Highest-Impact Plugin

Anthropic's official docs call LSP/code intelligence "the single highest-impact plugin you can install." With LSP enabled:

- Claude gets **automatic diagnostics** after every file edit (type errors, unused imports, missing returns)
- Errors surface immediately, not at build time
- Claude self-corrects without you noticing

If your editor supports it, enable LSP integration before spending time on CLAUDE.md test rules.

## The Verification Loop

The ideal workflow is:

```
1. Claude reads the relevant code (anti-hallucination)
2. Claude makes minimal changes (scope control)
3. Claude runs tests (verification)
4. If tests fail → Claude reads the error, fixes, re-runs
5. If tests pass → Claude commits
```

Steps 3-4 are the "verification loop." Each iteration costs tokens but catches bugs exponentially. Anthropic's internal teams report this pattern as their primary quality driver.

## Common Test Rule Patterns

### For projects with existing tests:
```markdown
- Run `pnpm test` after changes. Fix any failures before considering done.
- Do not modify existing test assertions. If tests fail after your change,
  the change is wrong, not the tests (unless I specifically asked to change test behavior).
```

### For projects without tests:
```markdown
- For new functions, write at least one test covering the happy path and
  one edge case. Place tests in __tests__/ adjacent to the source file.
```

### For CI/CD projects:
```markdown
- Before committing, verify: `pnpm lint && pnpm tsc --noEmit && pnpm test`
  All three must pass.
```

## Sources

- Anthropic Official Best Practices — code.claude.com/docs/en/best-practices
- Anthropic: "How Teams Use Claude Code" PDF — verification as highest-leverage practice
- Christopher Meiklejohn: "Claude Tested Everything Except..." — end-to-end verification
- Builder.io: "50 Claude Code Tips" — targeted test execution
- RanTheBuilder: "Lessons From Real Projects" — test-first debugging

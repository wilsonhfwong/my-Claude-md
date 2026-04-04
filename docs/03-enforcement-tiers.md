# The Three Enforcement Tiers

Not all rules are created equal. Claude Code has three distinct mechanisms for controlling behavior, each with different compliance guarantees.

## The Hierarchy

```
┌─────────────────────────────────────────────────┐
│  Tier 1: CLAUDE.md (Advisory)        ~70-80%    │
│  "Claude, please do X"                          │
│  → Claude reads it, tries to follow it          │
│  → No guarantee, especially if vague            │
├─────────────────────────────────────────────────┤
│  Tier 2: settings.json (Client-Enforced)  100%  │
│  permissions.allow / permissions.deny            │
│  → Enforced by the client, not the model        │
│  → Claude cannot bypass even if it wants to     │
├─────────────────────────────────────────────────┤
│  Tier 3: Hooks (Deterministic)           100%   │
│  PreToolUse / PostToolUse shell commands         │
│  → Runs before/after every matching tool use    │
│  → exit 1 = blocked, exit 0 = allowed           │
│  → Can auto-format, validate, gate commits      │
└─────────────────────────────────────────────────┘
```

## When to Use Which

| Requirement | Use | Example |
|-------------|-----|---------|
| "Prefer X over Y" | CLAUDE.md | "Use Zustand for client state, React Query for server state" |
| "Never do X" | Hook (PreToolUse) | Block commits on main branch |
| "Always format with X" | Hook (PostToolUse) | Run Prettier after every edit |
| "Block tool X entirely" | settings.json deny | `"Bash(rm -rf *)"` |
| "Allow only these commands" | settings.json allow | `"Bash(pnpm test*)"` |
| "Don't modify .env files" | settings.json deny | `"Edit(*.env*)"` |

### Decision Flowchart

```
Is this rule about code STYLE (formatting, indentation)?
  → Yes: Use a PostToolUse Hook with your formatter (100% compliance, 0 token cost)

Must this rule be followed EVERY time without exception?
  → Yes: Use a Hook or settings.json permission
  → No: CLAUDE.md is fine

Does Claude need to UNDERSTAND WHY?
  → Yes: Put it in CLAUDE.md (with optional Hook for enforcement)
  → No: Hook or settings.json alone is sufficient
```

## Tier 1: CLAUDE.md Rules (Advisory)

**Compliance**: ~70-80% for well-written rules, ~85-90% with CRITICAL/IMPORTANT emphasis

CLAUDE.md is for **guidance that requires judgment**. Claude reads it, understands the intent, and applies it contextually. But it's not enforced — Claude can and will occasionally ignore rules, especially when:

- The file is too long (>200 lines → compliance drops)
- Rules are vague ("write clean code")
- Rules conflict with each other
- Context window is getting full (>70% usage)

### What Works in CLAUDE.md

```markdown
- Before modifying any file, read it first.
- Do not invent function signatures. Grep for the actual interface.
- Functions must be under 40 lines. Extract helpers if longer.
- Throw AppError from src/errors.ts, never raw Error.
```

### What Doesn't Work in CLAUDE.md

```markdown
- Write clean, maintainable code.          ← Too vague, Claude already does this
- Use 2-space indentation.                  ← Use a formatter Hook instead
- Always use semicolons in JavaScript.      ← Use ESLint Hook instead
- Follow SOLID principles.                  ← Generic, adds no project-specific info
```

## Tier 2: settings.json Permissions (Client-Enforced)

**Compliance**: 100% — enforced by the client regardless of what Claude decides

```json
{
  "permissions": {
    "allow": [
      "Read", "Glob", "Grep",
      "Bash(pnpm build)", "Bash(pnpm test*)", "Bash(pnpm lint)",
      "Bash(git *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(pnpm publish*)",
      "Edit(*.env*)", "Write(*.env*)"
    ]
  }
}
```

Place in `.claude/settings.json` (project-level, committed) or `~/.claude/settings.json` (user-level).

## Tier 3: Hooks (Deterministic)

**Compliance**: 100% — shell commands that run automatically

### Auto-Format After Every Edit (PostToolUse)

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null || true"
    }]
  }
}
```

### Block Commits on Protected Branches (PreToolUse)

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+(push|commit)' && git branch --show-current | grep -qE '^(main|master)$'; then echo 'BLOCKED: Use a feature branch' >&2; exit 1; fi"
    }]
  }
}
```

### Block Access to Secrets Files (PreToolUse)

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write|Read",
      "command": "echo $CLAUDE_FILE_PATH | grep -qE '\\.(env|pem|key)$' && echo 'BLOCKED: Secrets file' >&2 && exit 1 || true"
    }]
  }
}
```

## The Community Lesson: Rules Alone Aren't Enough

From [GitHub Issue #29795](https://github.com/anthropics/claude-code/issues/29795) — a team documented **68 failures** where Claude violated CLAUDE.md rules, then built a 5-layer enforcement system:

```
Layer 5: HOOKS (hard blocks — cannot be bypassed)
Layer 4: AUTOMATED REVIEWS (5 tools, must pass before commit)
Layer 3: DECISION LOG (mandatory audit trail, hook-enforced)
Layer 2: FAIL DOCUMENTATION (68 documented failure patterns)
Layer 1: RULES & CONVENTIONS (CLAUDE.md)
```

Their conclusion: *"Text-based rules alone are insufficient. Claude reads them, appears to understand, then violates them anyway."* After adding Hooks for enforcement, violation rate dropped to near zero.

### The Recommended Pattern

For critical rules, use **both**:
- CLAUDE.md: so Claude understands **why** (and follows the rule ~80% of the time on its own)
- Hook: so the rule is **enforced** the other 20% of the time

```markdown
<!-- In CLAUDE.md -->
- CRITICAL: Never commit directly to main. Use feature branches.
```

```json
// In .claude/settings.json — Hook enforces the same rule
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+(push|commit)' && git branch --show-current | grep -q '^main$'; then echo 'BLOCKED: No commits on main' >&2; exit 1; fi"
    }]
  }
}
```

## Sources

- Anthropic Official Best Practices — code.claude.com/docs/en/best-practices
- GitHub Issue #29795: 5-Layer QA System from 68 Failures
- Jose Parreó García, "How Claude Code Rules Actually Work" (Substack)
- Dev.to: "5 Patterns That Make Claude Code Actually Follow Your Rules"
- Community-reported compliance rates (informal testing, not rigorous benchmarks)

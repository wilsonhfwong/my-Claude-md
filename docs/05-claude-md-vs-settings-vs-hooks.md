# CLAUDE.md vs Settings vs Hooks

Claude Code has three mechanisms for controlling behavior. Using the wrong one leads to either unenforced rules or wasted instruction budget.

## The Three Mechanisms

### CLAUDE.md -- Advisory Instructions (~70% Compliance)

CLAUDE.md provides **suggestions** that Claude follows most of the time but may occasionally deviate from, especially under complex conditions or deep context.

**Best for**:
- Coding conventions and architectural patterns
- Workflow preferences (which commands to run, which tools to use)
- Project context (tech stack, directory structure)
- Common mistakes to avoid

**Not suitable for**:
- Rules that must NEVER be violated (use Hooks)
- Tool permissions (use settings.json)
- Code formatting (use linter Hooks)

### settings.json -- Enforced Configuration (100% Compliance)

Settings control what Claude **can and cannot do**. These are hard boundaries, not suggestions.

**Best for**:
- Tool permissions (allow/deny file access, network, execution)
- MCP server configuration
- Environment variables
- Hook definitions
- Model selection

**Locations**:
```
~/.claude/settings.json              # Personal, all projects
./.claude/settings.json              # Project, shared (in git)
./.claude/settings.local.json        # Project, personal (gitignored)
```

### Hooks -- Deterministic Actions (100% Compliance)

Hooks are shell commands that run automatically before or after Claude's actions. They are not suggestions -- they execute every time, unconditionally.

**Best for**:
- Auto-formatting code after edits (Prettier, Black, gofmt)
- Running linters before commits
- Blocking writes to sensitive files (.env, credentials)
- Validating output before it's accepted
- Branch protection (prevent commits to main)

**Hook types**:
- `PreToolUse` -- runs before Claude uses a tool
- `PostToolUse` -- runs after Claude uses a tool
- `Notification` -- triggers on notifications
- `Stop` -- runs when Claude finishes a response

## Decision Flowchart

```
Is this rule about what Claude CAN/CANNOT access?
  └─ Yes → settings.json (permissions)

Must this rule be followed 100% of the time, no exceptions?
  └─ Yes → Is it a mechanical action (format, lint, validate)?
       └─ Yes → Hook
       └─ No  → Put in CLAUDE.md with CRITICAL emphasis + add a Hook as backup

Is this rule about coding style/formatting?
  └─ Yes → Hook (run formatter after edits)
            Don't waste CLAUDE.md instruction slots on formatting.

Is this rule task-specific (only matters sometimes)?
  └─ Yes → .claude/rules/*.md with conditional blocks

Is this a general project convention or workflow rule?
  └─ Yes → CLAUDE.md
```

## Side-by-Side Comparison

| Aspect | CLAUDE.md | settings.json | Hooks |
|--------|-----------|---------------|-------|
| Compliance | ~70% | 100% | 100% |
| Nature | Advisory | Configuration | Deterministic |
| Uses instruction budget | Yes | No | No |
| In version control | Yes | Yes (.claude/) | Yes (in settings) |
| Requires shell commands | No | No | Yes |
| When it runs | Every prompt | At startup | On specific events |

## Common Patterns

### Pattern 1: Format on Save (Hook, Not CLAUDE.md)

**Wrong** (wastes instruction budget, 70% compliance):
```markdown
# CLAUDE.md
- Format all code with Prettier before saving.
```

**Right** (100% compliance, zero instruction cost):
```json
// .claude/settings.json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "npx prettier --write $CLAUDE_FILE_PATH"
      }
    ]
  }
}
```

### Pattern 2: Branch Protection (Hook, Not CLAUDE.md)

**Wrong**:
```markdown
# CLAUDE.md
- **CRITICAL**: Never commit to main. Always use feature branches.
```

**Right** (add the CLAUDE.md rule too, but enforce with a Hook):
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "if git branch --show-current | grep -q '^main$'; then echo 'BLOCKED: Do not commit on main' >&2; exit 1; fi"
      }
    ]
  }
}
```

### Pattern 3: Architectural Rules (CLAUDE.md)

This genuinely belongs in CLAUDE.md because it requires judgment, not mechanical enforcement:

```markdown
# CLAUDE.md
- Database access goes through repos in src/repos/. No direct Prisma calls in handlers.
- API responses use the { data, error, meta } envelope from src/types/api.ts.
```

You could theoretically write a Hook that greps for `prisma.` in handler files, but it would be brittle. This is a judgment call best left as an advisory rule.

### Pattern 4: Sensitive File Protection (Hook)

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "echo $CLAUDE_FILE_PATH | grep -qE '\\.(env|pem|key)$' && echo 'BLOCKED: Cannot modify secrets' >&2 && exit 1 || true"
      }
    ]
  }
}
```

## The Distribution Strategy

A well-configured project uses all three:

```
CLAUDE.md (advisory, ~20-80 lines)
├── Project context (tech stack, structure)
├── Workflow rules (commands, conventions)
├── Architectural patterns (judgment calls)
└── Common mistakes to avoid

settings.json (enforced)
├── Tool permissions
├── MCP server config
└── Hook definitions
    ├── PostToolUse: auto-format after edits
    ├── PreToolUse: block sensitive file access
    └── PreToolUse: branch protection

.claude/rules/*.md (advisory, modular)
├── testing.md (test conventions)
├── api-design.md (API patterns)
└── deployment.md (deploy procedures)
```

**Key insight**: Every rule you move from CLAUDE.md to a Hook frees up an instruction slot for a rule that genuinely needs Claude's judgment.

## Next Steps

- [What Works and What Doesn't](06-what-works-and-what-doesnt.md) -- empirical findings
- [Advanced Techniques](07-advanced-techniques.md) -- multi-agent patterns and caching

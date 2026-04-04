# Hierarchy and Precedence

Claude Code loads instructions from multiple CLAUDE.md files at different levels. Understanding this hierarchy lets you put the right rules in the right place.

## The Four Layers

```
┌─────────────────────────────────────────────┐
│  Enterprise / Managed                       │  Highest priority
│  (MDM, registry, server-delivered policies) │  (overrides everything)
├─────────────────────────────────────────────┤
│  Project Level                              │
│  ./CLAUDE.md or ./.claude/CLAUDE.md         │  Shared with team (in git)
├─────────────────────────────────────────────┤
│  User Level                                 │
│  ~/.claude/CLAUDE.md                        │  Personal global defaults
├─────────────────────────────────────────────┤
│  (Base)                                     │  Lowest priority
│  Claude Code's built-in system prompt       │
└─────────────────────────────────────────────┘
```

## Layer Details

### Enterprise / Managed Level

Organization-wide policies delivered via MDM (macOS), Windows registry, or server configuration. These override all other settings. Most individual developers will never interact with this layer.

Use case: "All engineers must follow these security practices regardless of project."

### Project Level (Most Common)

The CLAUDE.md at your project root. This is where most rules live. It's committed to git and shared with your team.

Two equivalent locations:
- `./CLAUDE.md` (project root)
- `./.claude/CLAUDE.md` (inside the .claude directory)

If both exist, both are loaded.

### User Level

`~/.claude/CLAUDE.md` in your home directory. These rules apply to **every project** you work on. Use this for personal preferences that don't belong in any specific project.

Good candidates for user-level rules:
- Preferred commit message format
- Personal coding conventions
- Language preferences (e.g., "respond in Japanese")
- Default tools you always want used

### Subdirectory Level

CLAUDE.md files can exist in subdirectories. Claude discovers them by walking from the filesystem root down to the current working directory. More nested = higher priority.

```
my-monorepo/
  CLAUDE.md                    # Monorepo-wide rules
  packages/
    api/
      CLAUDE.md                # API-specific rules (overrides monorepo rules)
    frontend/
      CLAUDE.md                # Frontend-specific rules
```

## Modular Rules with `.claude/rules/*.md`

For larger projects, you can split rules into separate files:

```
.claude/
  rules/
    testing.md        # Test conventions
    api-design.md     # API design patterns
    deployment.md     # Deployment procedures
```

All files in `.claude/rules/` are loaded automatically. Subdirectories are processed recursively.

Benefits:
- Different team members can own different rule files
- Rules are organized by concern
- Easier to review in PRs (smaller diffs)
- Individual files can be conditionally relevant

## Precedence Rules

When rules conflict, **more specific wins**:

1. Enterprise overrides everything
2. Project overrides User
3. Subdirectory overrides parent directory
4. Within the same level, rules loaded later take slight precedence (end-of-prompt effect)

**Practical implication**: Put your personal preferences in `~/.claude/CLAUDE.md`. Put team standards in `./CLAUDE.md`. If a project needs to override your personal style, the project rules win.

## Settings Hierarchy

The same precedence applies to `.claude/settings.json`:

| File | Scope | In Git? |
|------|-------|---------|
| `~/.claude/settings.json` | All projects | No |
| `./.claude/settings.json` | This project, all users | Yes |
| `./.claude/settings.local.json` | This project, only you | No (gitignored) |

## Common Patterns

### Monorepo Setup
```
monorepo/
  CLAUDE.md                    # Shared conventions (language, commit style)
  .claude/
    rules/
      ci.md                    # CI/CD rules
  packages/
    service-a/
      CLAUDE.md                # Service-specific rules
    service-b/
      CLAUDE.md                # Service-specific rules
```

### Personal + Team
```
~/.claude/CLAUDE.md            # "I prefer concise responses"
project/CLAUDE.md              # "Use pnpm. Tests use vitest."
```

The team rules and personal rules combine. If they conflict, the project rules win.

## Next Steps

- [How Claude Reads Instructions](03-how-claude-reads-instructions.md) -- understand why rule placement matters
- [Writing Effective Rules](04-writing-effective-rules.md) -- techniques for rules that stick

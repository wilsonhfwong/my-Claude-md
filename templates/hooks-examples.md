# Common Hook Patterns

Hooks are shell commands defined in `.claude/settings.json` that run before or after Claude's actions. They provide 100% compliance enforcement at zero instruction-budget cost.

## Hook Types

| Type | When It Runs | Use For |
|------|-------------|---------|
| `PreToolUse` | Before Claude uses a tool | Blocking dangerous actions |
| `PostToolUse` | After Claude uses a tool | Auto-formatting, validation |
| `Notification` | On notifications | Custom alerting |
| `Stop` | When Claude finishes a response | Post-response checks |

## Available Variables

- `$CLAUDE_FILE_PATH` -- The file being edited/written (Edit, Write tools)
- `$CLAUDE_TOOL_INPUT` -- The full input to the tool
- `$CLAUDE_TOOL_NAME` -- Name of the tool being used

## Pattern 1: Auto-Format After Edits

Run your formatter automatically after every file edit.

### Prettier (JavaScript/TypeScript)
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null || true"
      }
    ]
  }
}
```

### Black (Python)
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "black $CLAUDE_FILE_PATH 2>/dev/null || true"
      }
    ]
  }
}
```

### gofmt (Go)
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "gofmt -w $CLAUDE_FILE_PATH 2>/dev/null || true"
      }
    ]
  }
}
```

### Rustfmt (Rust)
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "rustfmt $CLAUDE_FILE_PATH 2>/dev/null || true"
      }
    ]
  }
}
```

## Pattern 2: Branch Protection

Prevent commits and pushes on protected branches.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+(push|commit)' && git branch --show-current | grep -qE '^(main|master|release/.*)$'; then echo 'BLOCKED: Protected branch. Use a feature branch.' >&2; exit 1; fi"
      }
    ]
  }
}
```

## Pattern 3: Sensitive File Protection

Block reads/writes to files containing secrets.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Read",
        "command": "echo $CLAUDE_FILE_PATH | grep -qE '\\.(env|pem|key|secret)$|credentials' && echo 'BLOCKED: Cannot access secrets file' >&2 && exit 1 || true"
      }
    ]
  }
}
```

## Pattern 4: Lint After Edit

Run a fast linter check after every edit to catch issues immediately.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "if echo $CLAUDE_FILE_PATH | grep -qE '\\.(ts|tsx)$'; then npx eslint --fix $CLAUDE_FILE_PATH 2>/dev/null || true; fi"
      }
    ]
  }
}
```

## Pattern 5: Test Validation Before Commit

Run tests before allowing a commit.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+commit'; then npm test 2>&1 || (echo 'BLOCKED: Tests must pass before committing' >&2; exit 1); fi"
      }
    ]
  }
}
```

## Pattern 6: Force Commit Message Format

Ensure commits follow Conventional Commits format.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+commit\\s+-m'; then echo \"$CLAUDE_TOOL_INPUT\" | grep -qE '(feat|fix|docs|style|refactor|test|chore)(\\(.+\\))?:' || (echo 'BLOCKED: Commit message must follow Conventional Commits format' >&2; exit 1); fi"
      }
    ]
  }
}
```

## Combining Multiple Hooks

You can have multiple hooks of the same type. They run in order:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "command": "npx prettier --write $CLAUDE_FILE_PATH 2>/dev/null || true"
      },
      {
        "matcher": "Edit|Write",
        "command": "npx eslint --fix $CLAUDE_FILE_PATH 2>/dev/null || true"
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit|Write|Read",
        "command": "echo $CLAUDE_FILE_PATH | grep -qE '\\.(env|pem|key)$' && echo 'BLOCKED: Secrets file' >&2 && exit 1 || true"
      },
      {
        "matcher": "Bash",
        "command": "if git branch --show-current | grep -q '^main$'; then echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+(push|commit)' && echo 'BLOCKED: Protected branch' >&2 && exit 1 || true; fi"
      }
    ]
  }
}
```

## Tips

- Always add `2>/dev/null || true` to PostToolUse formatters so they don't block on non-applicable files
- PreToolUse hooks should `exit 1` to block the action, or `exit 0` / `true` to allow it
- Keep hooks fast -- they run on every matching tool use
- Test hooks manually before committing: run the command in your terminal first
- Hooks are defined in settings.json, not CLAUDE.md -- they're enforced, not advisory

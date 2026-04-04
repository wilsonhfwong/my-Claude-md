# How Claude Code Works Internally

Understanding the internals helps you write rules that actually stick. This chapter is based on source code analysis of `prompts.ts` (914 lines of TypeScript) and Anthropic's official context window documentation.

## The Prompt is an Operating System

Claude Code's system prompt is not a string. It's a **prompt assembly engine** with 15+ modular section builders, a cache boundary, and conditional logic.

```
getSystemPrompt() returns string[] →

  ┌─── STATIC (cacheable across users) ─────────────────┐
  │ getSimpleIntroSection()       → Opening + safety     │
  │ getSimpleSystemSection()      → Permissions, hooks   │
  │ getSimpleDoingTasksSection()  → Task execution guide │
  │ getActionsSection()           → High-risk controls   │
  │ getUsingYourToolsSection()    → Tool strategy        │
  │ getSimpleToneAndStyleSection()→ Tone/style           │
  │ getOutputEfficiencySection()  → Output efficiency    │
  ├─── CACHE BOUNDARY ──────────────────────────────────-┤
  │ session_guidance  → Tool/agent/skill routing         │
  │ memory            → loadMemoryPrompt() module        │
  │ env_info          → CWD, git, platform, model        │
  │ language          → User language preference          │
  │ mcp_instructions  → MCP server instructions          │
  │ YOUR CLAUDE.md    → Injected as user message          │
  └──────────────────────────────────────────────────────┘
```

**Source**: Wisely Chen, "拆解 Claude Code 的 System Prompt 源碼" (April 2026)

## Token Budget at Startup

| Component | Tokens | Priority |
|-----------|--------|----------|
| System prompt (built-in) | **4,200** | Highest (system message) |
| Auto memory (MEMORY.md) | ~680 | Hidden |
| Environment info | ~280 | Hidden |
| MCP tool names | ~120 | Deferred |
| Skill descriptions | ~450 | Lost after `/compact` |
| ~/.claude/CLAUDE.md (user) | ~320 | User message |
| Project CLAUDE.md | ~1,800 | User message |
| **Total startup** | **~7,850** | |
| **Total context window** | **200,000** | |

**Source**: Anthropic context window simulation (code.claude.com/docs/en/context-window)

### What This Means for You

- Your CLAUDE.md competes with 4,200 tokens of built-in rules
- The system prompt already handles: safety, tool use, response formatting, general coding conventions
- **Don't duplicate what's already there.** "Write clean code" wastes a slot — Claude already has instructions for that
- **Add what's NOT there**: your project's specific commands, patterns, and common mistakes

## The Cache Boundary

`SYSTEM_PROMPT_DYNAMIC_BOUNDARY` splits the prompt into two halves:

**Above the boundary (static)**: Behavior rules, tool strategy, tone, output efficiency. Cached globally across all users and sessions. Changing these sections requires a code deploy.

**Below the boundary (dynamic)**: Memory, environment info, MCP instructions, your CLAUDE.md. Recalculated every turn. This is why CLAUDE.md survives `/compact` — it's re-read from disk.

### Implication

Your CLAUDE.md is in the **dynamic half**, loaded after the static instructions. Due to the recency effect (LLMs pay more attention to recently-loaded content), your rules actually get decent attention — but they still have lower priority than the system prompt because they're delivered as user messages, not system messages.

**If you need system-prompt-level priority**, use `--append-system-prompt` (but this must be passed every invocation, so it's impractical for team use).

## CLAUDE.md is NOT Part of the System Prompt

This is the most important architectural fact:

> CLAUDE.md content is delivered as a **user message** after the system prompt, not as part of the system prompt itself.

This means:
- CLAUDE.md is **advisory**, not enforced
- Compliance is ~70-80% for well-written rules
- For 100% enforcement, use Hooks or settings.json permissions
- Vague or conflicting instructions get ignored

## What Survives `/compact`

| Content | Survives? | Notes |
|---------|-----------|-------|
| CLAUDE.md | Yes | Re-read from disk and re-injected |
| Auto memory | Yes | Re-loaded from MEMORY.md |
| System prompt | Yes | Always present |
| Skill descriptions | **No** | `noSurviveCompact: true` |
| Conversation history | **Compressed** | Reduced to ~12% of original tokens |
| In-conversation instructions | **Lost** | If it's not in CLAUDE.md, it won't survive |

**Key insight**: Any behavioral rule you care about **must be in CLAUDE.md**, not just stated in conversation. After compaction, conversation-only instructions vanish.

## CLAUDE.md Loading Order

Claude walks **up the directory tree** from the current working directory:

1. `./CLAUDE.md` loads first
2. `../CLAUDE.md` loads next
3. All the way up to the repo root
4. `CLAUDE.local.md` appended after `CLAUDE.md` at each level
5. Subdirectory CLAUDE.md files load **on demand** (when Claude reads files there)

**Priority** (last-read wins):
1. Managed policy (enterprise) — cannot be excluded
2. Project CLAUDE.md — highest priority for most users
3. User ~/.claude/CLAUDE.md — personal defaults
4. CLAUDE.local.md — personal overrides (gitignored)

HTML comments (`<!-- -->`) are **stripped** before injection, saving tokens. Use them for human-only notes.

## Subagent Architecture

Subagents (launched via the Agent tool) get their **own separate context**:

| Property | Main Session | Subagent |
|----------|-------------|----------|
| System prompt | 4,200 tokens | **900 tokens** (shorter) |
| CLAUDE.md | Loaded | Loaded (counts against subagent context) |
| Conversation history | Full | **None** (starts fresh) |
| Auto memory | Loaded | **Not loaded** |
| Built-in Explore/Plan | N/A | **Skip CLAUDE.md** for smaller context |

**Implication**: Put behavioral rules in the main CLAUDE.md. Subagents inherit them. Don't duplicate rules into agent prompts.

## The ANT Internal vs External Split

Anthropic employees (`USER_TYPE === 'ant'`) see different prompts. This matters because it reveals what Anthropic is testing:

| Dimension | External (You) | Internal (ANT) |
|-----------|---------------|----------------|
| Tone | "Be as short as possible" | "Clarity > brevity" |
| Length limits | Qualitative ("be concise") | **Quantified** ("≤25 words between tools, ≤100 words final") |
| Comments | Add as needed | Default none, only write WHY |
| Error handling | General guidance | Explicitly forbidden to fake passing results |

**Takeaway**: Anthropic's own team uses **quantified constraints**. Consider doing the same: "Functions ≤40 lines" beats "keep functions short."

Source code comment: `// @[MODEL LAUNCH]: un-gate once validated on external via A/B` — they A/B test internally before rolling out to external users.

## Sources

- Wisely Chen, "拆解 Claude Code 的 System Prompt 源碼" (April 2026) — prompts.ts analysis
- Anthropic, context window simulation — code.claude.com/docs/en/context-window
- Anthropic, How Claude Code works — code.claude.com/docs/en/how-claude-code-works
- Anthropic, Memory documentation — code.claude.com/docs/en/memory

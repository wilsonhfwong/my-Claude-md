# How Claude Code Works Internally

Understanding the internals helps you write rules that actually stick. This chapter is based on the leaked `prompts.ts` source code (914 lines of TypeScript), 12 deep-analysis articles from the March 2026 source map leak (512,237 lines, 1,902 files), and Anthropic's official context window documentation.

## The Codebase: What Was Revealed

On March 31, 2026, Claude Code v2.1.88 shipped to npm with a 59.8 MB source map (`cli.js.map`) intact. The complete unobfuscated TypeScript source was exposed: **512,237 lines across 1,902 files**. Key components:

- `prompts.ts` (914 lines) — the prompt assembly engine
- `query.ts` (~785KB) — the main agent loop (QueryEngine)
- `bashSecurity.ts` + `bashParser.ts` (~300KB combined) — shell security
- `Tool.ts` — each tool implements `validateInput()`, `checkPermissions()`, `call()`
- **101 command modules**, **130+ UI components**, **89 feature flags**

## The Prompt is an Operating System

Claude Code's system prompt is not a string. It's a **prompt assembly engine** with 15+ modular section builders, a cache boundary, and conditional logic. There are **110+ prompt strings** conditionally loaded, not one monolithic prompt.

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

**Sources**: Wisely Chen, Piebald-AI/claude-code-system-prompts, ComeOnOliver/claude-code-analysis

## Token Budget at Startup

| Component | Tokens | Priority |
|-----------|--------|----------|
| System prompt (built-in) | **4,200** | Highest (system message) |
| Auto memory (MEMORY.md) | ~680 | Hidden |
| Environment info | ~280 | Hidden |
| MCP tool **names only** | ~50 | Deferred (schemas load on-demand) |
| Skill descriptions | ~450 | Lost after `/compact` |
| ~/.claude/CLAUDE.md (user) | ~320 | User message |
| Project CLAUDE.md | ~1,800 | User message |
| **Total startup** | **~7,780** | |
| **Total context window** | **200,000** | |

**Key detail**: Tool schemas are **NOT** in the system prompt — only tool names (~50 tokens). Full JSON schemas load on-demand via `ToolSearchTool`. This is why the system prompt is "only" 4,200 tokens despite Claude Code having 24+ builtin tools.

**Source**: Anthropic context window simulation, ComeOnOliver/claude-code-analysis

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

This is the most important architectural fact. From the source code (`utils/api.ts:449-474`):

> CLAUDE.md content is injected via `prependUserContext()` as a **user message** after the system prompt, not as part of the system prompt itself.

This means:
- CLAUDE.md is **advisory**, not enforced
- Compliance is ~70-80% for well-written rules
- For 100% enforcement, use Hooks or settings.json permissions
- Vague or conflicting instructions get ignored
- Modifying CLAUDE.md does **not** invalidate the system prompt cache (it's in a separate layer)

**Source**: LINUX DO thread ("From Source Code Understanding CLAUDE.md"), gopenai blog

## CLAUDE.md is Session-Level, Not Per-Turn

A common misconception: CLAUDE.md is loaded **once at session start**, not re-read on every message. It is re-read only after:
- `/compact` (re-injected fresh from disk)
- `/clear` (new session)
- Session restart

This is why changes to CLAUDE.md mid-session don't take effect until the next compaction or restart.

**Source**: gopenai blog, LINUX DO thread

## What Survives Compaction

Claude Code has **three compression strategies** (not one):

1. **MicroCompact** — lightweight summarization for minor overflow
2. **AutoCompact** — standard summarization (conversation → ~12% of original tokens)
3. **Full Compact** — aggressive restructuring via `contextCollapse`

Plus **AutoDream** — a 4-phase memory consolidation that runs during idle/sleep (part of the KAIROS feature).

| Content | Survives? | Notes |
|---------|-----------|-------|
| CLAUDE.md | Yes | Re-read from disk and re-injected |
| Auto memory | Yes | Re-loaded from MEMORY.md |
| System prompt | Yes | Always present |
| Skill descriptions | **No** | `noSurviveCompact: true` |
| Conversation history | **Compressed** | Reduced to ~12% of original tokens |
| In-conversation instructions | **Lost** | If it's not in CLAUDE.md, it won't survive |

**Key insight**: Any behavioral rule you care about **must be in CLAUDE.md**, not just stated in conversation.

**Warning from the source code**: A comment in `autoCompact.ts` revealed that **1,279 sessions** experienced 50+ consecutive auto-compaction failures (up to 3,272 per session), wasting ~**250,000 API calls/day** globally. Long sessions with heavy tool use can trigger pathological compaction loops.

**Source**: sanbuphy/claude-code-source-code, awesome-claude-code-postleak-insights

## CLAUDE.md Loading Order

Claude walks **up the directory tree** from the current working directory, checking `CLAUDE.md`, `.claude/CLAUDE.md`, and `.claude/rules/*.md` at each level:

1. `./CLAUDE.md` loads first
2. `../CLAUDE.md` loads next
3. All the way up to the repo root
4. `CLAUDE.local.md` appended after `CLAUDE.md` at each level
5. Subdirectory CLAUDE.md files load **on demand** (when Claude reads files there)
6. Global: `~/.claude/CLAUDE.md` and `/etc/claude-code/CLAUDE.md`

**Priority** (last-read wins):
1. Managed policy (enterprise, `/etc/claude-code/CLAUDE.md`) — cannot be excluded
2. Project CLAUDE.md — highest priority for most users
3. User ~/.claude/CLAUDE.md — personal defaults
4. CLAUDE.local.md — personal overrides (gitignored)

HTML comments (`<!-- -->`) are **stripped** before injection, saving tokens. Use them for human-only notes.

**Source**: Yanchuk Gist, LINUX DO thread

## The Permission Pipeline

From the source code, permissions are enforced through a **4-stage pipeline**:

```
Stage 1: Static Rules (instant)
  → permissions.allow / permissions.deny in settings.json
  → Dangerous files (.gitconfig, .bashrc, .mcp.json) blocked regardless

Stage 2: Mode-Based Checks (instant)
  → Auto-mode, plan-mode, REPL-mode each have different defaults

Stage 3: LLM Classifier (auto-mode only)
  → Uses Haiku to classify tool calls as safe/unsafe
  → Fast and cheap, but not 100% accurate

Stage 4: User Prompt (blocking)
  → "Allow / Deny" dialog shown to user
  → Denial circuit breaker: >3 consecutive or >20 total denials
    triggers fallback to always-prompt mode
```

**Implication**: Your settings.json `permissions.deny` rules execute at Stage 1 — they're checked **before** Claude even sees the request. This is why they're 100% reliable.

**Source**: Yanchuk Gist

## Subagent Architecture

Subagents get their **own separate context** — they do **NOT** inherit the parent session's conversation or CLAUDE.md automatically.

| Property | Main Session | Subagent |
|----------|-------------|----------|
| System prompt | 4,200 tokens | **900 tokens** (shorter) |
| CLAUDE.md | Loaded | **Not shared** (fresh context) |
| Conversation history | Full | **None** (starts fresh) |
| Auto memory | Loaded | **Not loaded** |
| Built-in Explore/Plan | N/A | **Skip CLAUDE.md** for smaller context |

Sub-agent token budgets vary by type:
- Explore agent: 494 tokens
- Plan agent: 636 tokens
- CLAUDE.md creation agent: 384 tokens
- Security review: 2,607 tokens
- Schedule (remote cron): 2,486 tokens

Sub-agent modes: **in-process** (default), **fork** (subprocess), **worktree** (isolated git), **remote** (via bridge).

**Implication**: If you need sub-agents to follow specific rules, those rules must be encoded in agent task descriptions, not just CLAUDE.md. The built-in Explore and Plan agents explicitly skip CLAUDE.md loading.

**Source**: Piebald-AI/claude-code-system-prompts, sanbuphy/claude-code-source-code, gopenai blog

## The ANT Internal vs External Split

Anthropic employees (`USER_TYPE === 'ant'`) see different prompts. The flag appears **150+ times** in the source. Key differences:

| Dimension | External (You) | Internal (ANT) |
|-----------|---------------|----------------|
| Tone | "Be as short as possible" | "Clarity > brevity" |
| Length limits | Qualitative ("be concise") | **Quantified** ("≤25 words between tools, ≤100 words final") |
| Comments | Add as needed | Default none, only write WHY |
| Error handling | General guidance | Explicitly forbidden to fake passing results |
| A/B testing | Gets validated features | Gets experimental features first |

**Takeaway**: Anthropic's own team uses **quantified constraints**. Consider doing the same: "Functions ≤40 lines" beats "keep functions short."

Source code comment: `// @[MODEL LAUNCH]: un-gate once validated on external via A/B` — features are A/B tested internally before external rollout. GrowthBook is used for feature flag management.

## Hidden Systems Worth Knowing About

### Silent Sonnet Downgrade

**3 consecutive 529 (overloaded) errors** trigger an automatic, silent downgrade from Opus to Sonnet. This explains sudden quality drops mid-session. There is no user notification.

**Source**: gopenai blog

### Anti-Distillation

In `claude.ts`, the `ANTI_DISTILLATION_CC` flag sends instructions to inject **decoy tool definitions** into API responses — poisoning any training data scraped from API traffic.

### Frustration Detection

`userPromptKeywords.ts` contains a regex matching profanity and frustration keywords ("wtf", "ffs", "horrible", "this sucks") — likely used for analytics or behavior adjustment.

### KAIROS / Dream Mode

A feature flag referenced 150+ times. Implements autonomous daemon mode: background agent running after terminal close, with `/dream` skill for nightly memory distillation and GitHub webhook subscriptions.

**Source**: Alex Kim's analysis, Deep-Dive-Claude-Code

## Sources

### Source Code Analysis
- Wisely Chen, "拆解 Claude Code 的 System Prompt 源碼" (April 2026)
- [Alex Kim: Fake tools, frustration regexes, undercover mode](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/)
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — 110+ prompt strings, 141 versions tracked
- [sanbuphy/claude-code-source-code](https://github.com/sanbuphy/claude-code-source-code) — Chinese README, architecture analysis
- [lintsinghua/claude-code-book](https://github.com/lintsinghua/claude-code-book) — 420K-character, 15-chapter architecture book
- [Deep-Dive-Claude-Code](https://github.com/waiterxiaoyy/Deep-Dive-Claude-Code) — 13-chapter interactive analysis
- [ComeOnOliver/claude-code-analysis](https://github.com/ComeOnOliver/claude-code-analysis) — reverse-engineering documentation
- [Yanchuk Gist: Complete Architecture Deep Dive](https://gist.github.com/yanchuk/0c47dd351c2805236e44ec3935e9095d)
- [awesome-claude-code-postleak-insights](https://github.com/nblintao/awesome-claude-code-postleak-insights)

### Community Analysis
- [LINUX DO: Understanding CLAUDE.md from source](https://linux.do/t/topic/1871216)
- [gopenai: What the leak says about usage](https://blog.gopenai.com/the-accidental-open-source-what-claude-codes-leaked-source-says-about-how-you-should-be-using-it-6f640e501835)
- [Engineers Codex: Diving into source](https://read.engineerscodex.com/p/diving-into-claude-codes-source-code)
- Juejin.cn: 4 articles analyzing the leak

### Official Documentation
- Anthropic, context window simulation — code.claude.com/docs/en/context-window
- Anthropic, How Claude Code works — code.claude.com/docs/en/how-claude-code-works
- Anthropic, Memory documentation — code.claude.com/docs/en/memory

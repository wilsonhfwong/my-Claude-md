# How Claude Reads Your Instructions

Understanding how Claude Code processes CLAUDE.md internally helps you write rules that stick. This section covers what the community has learned from official documentation, empirical testing, and source code analysis.

> **Note**: Some observations here come from community reverse-engineering (including the March 2026 source code leak) and may change with future updates. Focus on the practical takeaways, not the exact numbers.

## The Instruction Budget

Claude Code's system prompt (tool definitions, safety rules, behavioral guidelines) consumes roughly **50 instruction slots** before your CLAUDE.md is even loaded.

Frontier LLMs follow approximately **150-200 total instructions** before compliance begins to degrade -- not catastrophically, but uniformly. Each additional rule slightly dilutes all other rules.

**Your budget: ~100-150 instruction slots for all your CLAUDE.md rules combined.**

This is why a focused 50-line CLAUDE.md outperforms a 500-line one. It's not that Claude ignores long files -- it's that every low-value rule makes every high-value rule slightly less likely to be followed.

### Practical Takeaway

Count your rules. If you have more than 150, you're past the point of diminishing returns. Prioritize the top 20 that matter most.

## Token Overhead

Before your first message, Claude Code loads:
- System prompt: ~15-20K tokens
- Tool definitions (built-in + MCP): ~5-15K tokens
- Your CLAUDE.md files: varies (a 200-line file is ~1,500-2,000 tokens)

**Total baseline: ~25-35K tokens** out of a 200K context window.

A bloated CLAUDE.md doesn't just waste instruction slots -- it eats into the context window available for your actual conversation, code, and tool results.

## Prompt Caching

Anthropic uses prompt caching to reduce costs and latency. The system prompt + CLAUDE.md content is treated as a cacheable prefix. Once cached, subsequent turns in the same session reuse the cached prefix at ~10x lower cost.

### What Breaks the Cache

Any change to the prompt prefix invalidates the cache from that point forward:
- **Adding MCP tools mid-session** -- inserts new tool definitions
- **Timestamps in CLAUDE.md** -- if your CLAUDE.md includes dynamic dates, every session gets a cache miss
- **Switching models mid-session** -- different model = different cache key
- **Editing CLAUDE.md during a session** -- forces a full re-read

### Practical Takeaway

Keep your CLAUDE.md **static**. Avoid dynamic content (dates, counters, session-specific notes). If you need to change rules mid-session, batch your edits rather than making frequent small changes.

## The End-of-Prompt Effect

LLMs give slightly more attention to instructions appearing **later** in the prompt. This is a well-documented phenomenon in the research literature (sometimes called "recency bias" in instruction following).

In Claude Code's architecture:
1. System prompt loads first (earliest in context)
2. CLAUDE.md loads after system prompt
3. Within CLAUDE.md, rules at the bottom appear later

### Practical Takeaway

Put your **most critical rules last** in your CLAUDE.md. Safety guardrails, absolute prohibitions, and the rules you care most about belong at the end of the file, not the beginning.

However, don't over-optimize for this. The effect is subtle, not dramatic. A well-written rule near the top still works. A poorly-written rule at the bottom still fails.

## Memory Indexing

Claude Code maintains a 3-layer memory index system. Each entry is summarized with a **~150-character pointer** -- a terse description used for retrieval.

This has implications for how you write rules:
- **Self-contained rules** are easier to index and retrieve than rules that depend on surrounding context
- **Keyword-rich rules** are more reliably matched to relevant situations
- **Short, declarative statements** index better than verbose paragraphs

### Good (Easy to Index)
```
Use `pnpm`, not `npm`. The lockfile is pnpm-lock.yaml.
```

### Bad (Hard to Index)
```
When working on this project, please be aware that we've standardized on
pnpm as our package manager of choice. This decision was made in Q3 2025
after evaluating several options, and the team agreed that...
```

The first version is one sentence with clear keywords (`pnpm`, `npm`, `lockfile`). The second buries the actionable instruction in narrative.

## The "May or May Not Be Relevant" Filter

Claude Code's system prompt includes a note that CLAUDE.md context "may or may not be relevant to your tasks." This means Claude actively evaluates whether each rule applies to the current situation.

### Practical Takeaway

Rules that are clearly scoped to specific situations are more likely to be followed when relevant and ignored when not. Use conditional blocks for task-specific rules:

```markdown
<important if="modifying database schema">
Always create a migration file. Never modify the schema directly.
Run `pnpm prisma migrate dev` to test migrations locally.
</important>
```

## Summary of Practical Rules

| Principle | Action |
|-----------|--------|
| Instruction budget is ~100-150 | Count your rules; cut the weak ones |
| Token overhead is 25-35K | Keep CLAUDE.md under 200 lines |
| Prompt caching saves 10x cost | Keep content static; avoid dynamic data |
| End-of-prompt gets more attention | Put critical rules last |
| Memory uses ~150-char pointers | Write terse, keyword-rich rules |
| Relevance filtering is active | Scope rules with conditional blocks |

## Next Steps

- [Writing Effective Rules](04-writing-effective-rules.md) -- techniques for rules that Claude actually follows
- [Advanced Techniques](07-advanced-techniques.md) -- prompt caching optimization in depth

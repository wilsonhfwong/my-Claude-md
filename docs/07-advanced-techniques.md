# Advanced Techniques

For power users who want to squeeze maximum value from their Claude Code configuration.

## Prompt Caching Optimization

Anthropic caches the static prefix of each conversation (system prompt + CLAUDE.md + tool definitions). Cached input costs ~10x less ($0.50 vs $5 per million tokens for Opus).

### How to Maximize Cache Hits

**Order matters.** The cache is invalidated from the first byte that changes. Structure your CLAUDE.md so stable content comes first:

```markdown
# Project: Acme API                          ← Stable (rarely changes)
TypeScript + Express + Prisma + PostgreSQL.

## Commands                                   ← Stable
- Build: `pnpm build`
- Test: `pnpm test`

## Rules                                      ← Stable
- Use pnpm, not npm.
- Throw AppError, not raw Error.

## Current Focus                              ← Volatile (if you must include it)
- Working on the payments integration.
```

If the volatile section is at the end, everything before it stays cached.

### What Invalidates the Cache

| Action | Cache Impact |
|--------|-------------|
| Normal conversation turns | No impact (cache is reused) |
| Editing CLAUDE.md mid-session | Full invalidation from change point |
| Adding/removing MCP tools | Full invalidation |
| Switching models | Full invalidation |
| Dynamic timestamps in CLAUDE.md | Miss every session |

**Practical rule**: Don't edit CLAUDE.md mid-session. If you must, batch changes into one edit. Each edit costs a full cache rebuild for that turn.

### Cost Impact

For a typical session with 50 turns:
- With caching: ~49 turns use cached prefix (~$0.50/M rate)
- Without caching: all 50 turns at full price (~$5/M rate)
- A 200-line CLAUDE.md adds ~2K tokens to the prefix = ~$0.001 per cached turn

The cost of a well-sized CLAUDE.md is negligible. The cost of cache invalidation is not.

## Multi-Agent Patterns

Claude Code can spawn subagents for focused tasks. Your CLAUDE.md applies to the main agent; subagents inherit a subset of context.

### Model Selection Strategy

```bash
# Main agent: Opus (complex reasoning, architecture)
# Subagents: Sonnet (focused tasks, faster, cheaper)
export CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-4-6
```

Use cases for subagents:
- Running tests and reporting results
- Searching the codebase for specific patterns
- Generating boilerplate code from templates
- Performing focused code reviews

### CLAUDE.md Implications

Rules in your CLAUDE.md affect the main agent. Subagents get a reduced context. If you have rules that matter for subagent tasks (like testing conventions), ensure they're also available in relevant `.claude/rules/*.md` files.

## Token Budget Management

### Calculating Your Budget

```
Context window:           200,000 tokens
System prompt:           -20,000 tokens (approximate)
Tool definitions:        -10,000 tokens (varies with MCP tools)
Your CLAUDE.md:           -2,000 tokens (200 lines)
────────────────────────────────────────
Available for conversation: ~168,000 tokens
```

Each MCP server you add contributes tool definitions that consume context. Five MCP servers might add 5-10K tokens of tool definitions.

### Monitoring Instruction Count

A quick health check:

```bash
# Count actionable rules in your CLAUDE.md
grep -cE '^\s*-\s' CLAUDE.md
```

If the count exceeds 100, start pruning. Remember: the system prompt already uses ~50 of your ~150-200 instruction budget.

### When Context Gets Compressed

In long sessions, Claude Code compresses earlier context to fit new information. When this happens:
- Early conversation turns are summarized
- Tool results may be truncated
- CLAUDE.md content is preserved (it's part of the prefix)

This is another reason to keep CLAUDE.md concise -- it's one of the few things guaranteed to survive context compression.

## Conditional Loading with Rules

Use `.claude/rules/*.md` to organize rules by concern. All files are loaded, but conditional blocks limit when they activate:

```
.claude/rules/
  backend.md      # Backend-specific rules
  frontend.md     # Frontend-specific rules
  testing.md      # Test conventions
  security.md     # Security requirements
```

Each file should be self-contained and focused:

```markdown
<!-- .claude/rules/testing.md -->
<important if="writing, modifying, or reviewing tests">
- Use `describe`/`it` blocks (not `test()`).
- Mock externals with `vi.mock()`. No real HTTP in tests.
- Each test file: at least one happy path + one error case.
- Test files live next to source: `foo.test.ts` beside `foo.ts`.
</important>
```

Benefits:
- Different team members own different rule files
- Clear separation of concerns
- Easier code review (smaller, focused diffs)
- Conditional blocks prevent irrelevant rules from consuming instruction budget

## The `/clear` Strategy

Long sessions accumulate context that can dilute CLAUDE.md effectiveness. Community consensus: use `/clear` aggressively.

- After completing a major task, `/clear` before starting the next
- When Claude starts ignoring rules it was following earlier
- Before switching between unrelated areas of the codebase
- After large tool results that consumed significant context

Each `/clear` resets the conversation while preserving CLAUDE.md (it's reloaded from the prefix). This gives your rules fresh attention.

## Skills for Specialized Knowledge

Skills are on-demand instruction sets that load only when invoked. They're ideal for knowledge that's too specialized for CLAUDE.md but too important to omit.

**Distribution pattern**:
- CLAUDE.md: Universal rules (loaded every session, costs instruction budget)
- Skills: Specialized knowledge (loaded on demand, no ongoing cost)
- Hooks: Mechanical enforcement (runs automatically, 100% compliance)

Example: Your CLAUDE.md says "Run `pnpm test` before committing." Your testing skill contains detailed test patterns, mocking strategies, and coverage requirements. The skill only loads when you're actually writing tests.

## Environment Variables for Configuration

Some Claude Code behavior can be tuned via environment variables:

```bash
# Override subagent model
export CLAUDE_CODE_SUBAGENT_MODEL=claude-sonnet-4-6

# Set default max turns for agentic tasks
export CLAUDE_CODE_MAX_TURNS=50
```

These don't consume instruction budget and are enforced at the runtime level.

## Next Steps

- [Maintenance Lifecycle](08-maintenance-lifecycle.md) -- keeping your configuration effective over time
- [Examples](../examples/) -- see these techniques applied in practice

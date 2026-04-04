# Quick Start: Your First Behavioral CLAUDE.md

Get a working CLAUDE.md in 5 minutes that makes Claude Code write better code.

## The Minimum Viable CLAUDE.md

Create a file called `CLAUDE.md` in your project root:

```markdown
# Rules

- If you are unsure whether a function, API, or library method exists, search the codebase or official docs first. Do not invent things.
- Before modifying any file, read it first. Understand existing code before making changes.
- Do not add features, refactors, or "improvements" beyond what was asked.
- Run tests after making changes. Do not consider a task complete until tests pass.
- If critical information is missing, ask me instead of guessing.
```

That's it. Five rules, each addressing a real failure mode.

## Why These Five Rules?

Each rule targets a specific, documented problem:

| Rule | Problem It Solves | Sources |
|------|------------------|---------|
| Don't invent things | Claude fabricates API methods, function signatures, library interfaces | Anthropic docs, LobeHub anti-hallucination skill, 20+ community reports |
| Read before writing | Claude modifies code it hasn't read, causing bugs | Anthropic official best practice, Boris Cherny |
| No unrequested changes | Claude over-engineers, adds features, refactors beyond scope | Builder.io, RanTheBuilder, AIMonks |
| Run tests | Claude declares "fixed" without verification | Christopher Meiklejohn, Anthropic internal teams |
| Ask don't guess | Claude silently makes wrong assumptions | HumanLayer, community consensus |

## How It Works Internally

When Claude Code starts a session:

1. System prompt loads (4,200 tokens, hidden, highest priority)
2. Auto memory loads (~680 tokens)
3. Environment info loads (~280 tokens)
4. **Your CLAUDE.md loads (~320-1,800 tokens, delivered as a user message)**
5. Your first prompt arrives

Your CLAUDE.md has **lower priority** than the built-in system prompt. This is why:
- Vague rules get ignored (the system prompt's 4,200 tokens dominate)
- Specific, concrete rules work (they add information the system prompt doesn't have)
- Fewer rules = higher compliance (each rule gets more attention)

## What To Do Next

1. **Use it for a week.** Note every time Claude makes a mistake.
2. **Add one rule per mistake.** Each correction becomes a permanent rule.
3. **After a month, prune.** Delete any rule Claude hasn't violated in 30 days.

This "start small, grow from pain" approach consistently produces better CLAUDE.md files than writing 50 rules upfront.

## Next Steps

- [How Claude Code Works Internally](02-system-prompt-internals.md) — understand the 914-line prompt engine
- [Anti-Hallucination Rules](04-anti-hallucination.md) — the most requested behavioral rules
- [What Actually Works](07-what-works-and-what-doesnt.md) — community-tested rules with compliance rates

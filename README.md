# CLAUDE.md Best Practices: Making Claude Code Write Better Code

A research-backed guide to writing CLAUDE.md rules that improve Claude Code's **coding behavior** — preventing hallucination, enforcing verification, controlling scope, and producing reliable code.

Based on **43+ sources**: Anthropic official docs, the March 2026 source map leak (512K lines of TypeScript), 12 deep-analysis articles of `prompts.ts` and the codebase internals, community experiments, academic research, and real-world battle testing.

## Who This Is For

- Developers who want Claude Code to **stop making things up** and say "I don't know" instead
- Teams tired of Claude **over-engineering**, adding unrequested features, or ignoring instructions
- Anyone who wants to understand **how Claude Code actually processes your rules** internally

## Start Here

New to CLAUDE.md? Begin with the **[Quick Start](docs/01-quick-start.md)** — a working behavioral CLAUDE.md in 5 minutes.

Already have a CLAUDE.md but Claude keeps misbehaving? Jump to **[What Actually Works](docs/06-what-works-and-what-doesnt.md)**.

## Table of Contents

### Understanding the Machine
1. [Quick Start](docs/01-quick-start.md) — Your first behavioral CLAUDE.md in 5 minutes
2. [How Claude Code Works Internally](docs/02-system-prompt-internals.md) — The 914-line prompt engine, cache boundary, token budgets
3. [The Three Enforcement Tiers](docs/03-enforcement-tiers.md) — CLAUDE.md (~70%) vs settings.json (100%) vs Hooks (100%)

### Behavioral Rules That Work
4. [Anti-Hallucination Rules](docs/04-anti-hallucination.md) — Stop Claude from inventing APIs, faking results, and guessing
5. [Scope Control](docs/05-scope-control.md) — Prevent over-engineering, unrequested features, and runaway refactors
6. [Testing and Verification](docs/06-testing-and-verification.md) — The single highest-leverage behavior change
7. [What Actually Works](docs/07-what-works-and-what-doesnt.md) — Community-tested rules with compliance rates

### Going Deeper
8. [Writing Rules That Stick](docs/08-writing-effective-rules.md) — Quantified constraints, distributed repetition, the Question Test
9. [Maintenance and Self-Improvement](docs/09-maintenance-lifecycle.md) — The living document loop

### Practical Resources
- [Examples](examples/) — Minimal, standard, and enterprise CLAUDE.md files (behavioral focus)
- [Templates](templates/) — Copy-paste starters with behavioral rules built in

## Key Takeaways (TL;DR)

1. **Claude Code's system prompt is 4,200 tokens**. Your CLAUDE.md is injected as a user message *after* it, with lower priority. Keep rules tight — every line competes for attention.
2. **Say "don't hallucinate" explicitly**. Without this, Claude invents function signatures, fabricates API methods, and guesses at library interfaces.
3. **"Read before writing" is the #1 rule**. Most bugs come from Claude modifying code it hasn't read.
4. **Quantified rules beat qualitative ones**. "≤40 lines per function" works; "keep functions short" doesn't.
5. **Three enforcement tiers**: CLAUDE.md is advisory (~70-80%). Hooks are deterministic (100%). Use the right tier.
6. **Start with 5 rules**. Add one per week when Claude makes a mistake. Prune monthly. This beats writing 50 rules upfront.
7. **The self-improving loop**: Every time Claude makes a mistake → add a rule → it never happens again.

## Sources

This guide synthesizes findings from 31+ sources including:
- [Anthropic Official Best Practices](https://code.claude.com/docs/en/best-practices)
- [Anthropic: How Teams Use Claude Code (PDF)](https://www-cdn.anthropic.com/58284b19e702b49db9302d5b6f135ad8871e7658.pdf)
- [prompts.ts Source Code Analysis](https://ai-coding.wiselychen.com/claude-code-system-prompt-source-code-analysis/) (Wisely Chen)
- [Boris Cherny (Claude Code Creator) Tips](https://x.com/bcherny/status/2007179832300581177)
- [arxiv 2511.09268: Decoding Configuration of AI Coding Agents](https://arxiv.org/abs/2511.09268)
- [5-Layer QA System from 68 Failures](https://github.com/anthropics/claude-code/issues/29795)
- [Alex Kim: Fake tools, frustration regexes, undercover mode](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/)
- [Piebald-AI/claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) — 110+ prompt strings extracted
- [Yanchuk Gist: Complete Architecture Deep Dive](https://gist.github.com/yanchuk/0c47dd351c2805236e44ec3935e9095d)
- [awesome-claude-code-postleak-insights](https://github.com/nblintao/awesome-claude-code-postleak-insights) — curated meta-list
- [lintsinghua/claude-code-book](https://github.com/lintsinghua/claude-code-book) — 420K-character architecture book
- And 30+ community articles, HN threads, blog posts, and Juejin/Zhihu analyses (full list in each doc)

## License

MIT

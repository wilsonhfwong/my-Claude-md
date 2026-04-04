# CLAUDE.md Best Practices Guide

A comprehensive guide to writing effective CLAUDE.md files for Claude Code, informed by official documentation, community experience, and insights from the Claude Code source code analysis (March 2026).

## Who This Is For

- Developers using Claude Code who want better results from their AI assistant
- Teams standardizing their Claude Code configuration
- Anyone curious about how Claude Code processes instructions internally

## Start Here

If you're new to CLAUDE.md, begin with the **[Quick Start Guide](docs/01-quick-start.md)** -- you'll have a working CLAUDE.md in 5 minutes.

## Table of Contents

### Fundamentals
1. [Quick Start](docs/01-quick-start.md) -- Your first CLAUDE.md in 5 minutes
2. [Hierarchy and Precedence](docs/02-hierarchy-and-precedence.md) -- The multi-layer configuration system
3. [How Claude Reads Instructions](docs/03-how-claude-reads-instructions.md) -- Internal processing model, instruction budgets, prompt caching

### Writing Effective Rules
4. [Writing Effective Rules](docs/04-writing-effective-rules.md) -- The Question Test, WHAT-WHY-HOW framework, sizing
5. [CLAUDE.md vs Settings vs Hooks](docs/05-claude-md-vs-settings-vs-hooks.md) -- When to use which mechanism
6. [What Works and What Doesn't](docs/06-what-works-and-what-doesnt.md) -- Empirical findings from the community

### Going Deeper
7. [Advanced Techniques](docs/07-advanced-techniques.md) -- Multi-agent patterns, caching optimization, token budgets
8. [Maintenance Lifecycle](docs/08-maintenance-lifecycle.md) -- Pruning cadence, team process, measuring effectiveness

### Practical Resources
- [Examples](examples/) -- Minimal, standard, and enterprise CLAUDE.md files
- [Templates](templates/) -- Copy-paste starters with placeholders

## Key Takeaways (TL;DR)

- **Keep it short**: 40-80 lines is ideal, under 200 is acceptable, over 500 is harmful
- **Question Test**: For every rule, ask "Would Claude make a mistake without this?" -- if no, delete it
- **Three compliance tiers**: CLAUDE.md (~70%), settings.json (100%), Hooks (100%)
- **Instruction budget**: You have ~100-150 instruction slots -- every unnecessary rule dilutes the ones that matter
- **Start small**: Begin with 5 rules, add one per week, prune monthly

## Contributing

This guide is a living document. If you discover new techniques or find errors, contributions are welcome.

## License

MIT

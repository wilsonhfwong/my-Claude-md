# What Actually Works (and What Doesn't)

Community-tested behavioral rules with observed compliance rates. Based on 31+ sources including Anthropic official docs, Hacker News threads, Dev.to articles, Medium posts, GitHub repos, and an academic paper.

## Rules That Work (High Compliance)

### Tier 1: Concrete, Measurable Rules (~80-90% compliance)

These rules work because they're **specific and verifiable**:

```markdown
- Functions must be under 40 lines. Extract helpers if longer.
- Never use `any` type in TypeScript. Use `unknown` and narrow with type guards.
- No console.log in production code. Use the logger from src/lib/logger.ts.
- Throw AppError from src/errors.ts, never raw Error.
- Parameterized queries only. Never concatenate user input into SQL.
- Files should be 200-400 lines typical, 800 max.
```

**Why they work**: Claude can self-check. "Is this function over 40 lines?" is a yes/no question. "Is this code clean?" is not.

### Tier 2: Behavioral Rules with CRITICAL/IMPORTANT (~85-90%)

Adding emphasis keywords boosts compliance, but **use sparingly** (2-3 max per file):

```markdown
- **CRITICAL**: Never commit .env files or hardcoded secrets.
- **CRITICAL**: All database migrations are forward-only. Never modify existing migrations.
- **IMPORTANT**: Never push directly to main or release/* branches.
```

**Warning**: If everything is CRITICAL, nothing is. The emphasis effect dilutes with overuse.

### Tier 3: Project-Specific Behavioral Rules (~70-80%)

```markdown
- Before modifying any file, read it first.
- Do not add features beyond what was requested.
- Run tests after making changes.
- If unsure, ask instead of guessing.
```

These get lower compliance because they require judgment, but they're still high-value because they address real failure modes.

## Rules That Don't Work (Low or Zero Compliance)

### Generic Guidelines (~0% marginal impact)

```markdown
# DON'T USE THESE — they add nothing
- Write clean, maintainable code.
- Follow SOLID principles.
- Use meaningful variable names.
- Handle errors properly.
- Write good documentation.
```

Claude already does all of these. Adding them wastes instruction budget on zero marginal improvement.

### Style Rules That Belong in Linters (~0% compliance benefit)

```markdown
# DON'T USE THESE — use a formatter Hook instead
- Use 2-space indentation.
- Always use semicolons.
- Prefer single quotes.
- Max line length 80 characters.
```

These get 100% compliance as a PostToolUse Hook running Prettier/ESLint, and 0 token cost. Putting them in CLAUDE.md wastes tokens for ~60% compliance.

### Personality Instructions (~0% impact)

```markdown
# DON'T USE THESE — wastes tokens
- You are a senior engineer.
- Think step by step.
- Be a 10x developer.
```

### Rules in Files Over 500 Lines (~30-50% compliance)

Community testing shows compliance drops significantly past 500 lines. At 1000+ lines, Claude may effectively ignore entire sections.

> "If Claude keeps doing something you don't want despite having a rule against it, the file is probably too long and the rule is getting lost." — Anthropic Memory docs

## Compliance Rate Summary

| Technique | Estimated Compliance |
|-----------|---------------------|
| Hook enforcement | ~100% |
| settings.json permissions | ~100% |
| CRITICAL/IMPORTANT rule (well-written, ≤3 per file) | ~85-90% |
| Concrete, measurable rule | ~80-90% |
| Standard behavioral rule (specific) | ~70-80% |
| Behavioral rule in >200 line file | ~50-70% |
| Vague behavioral rule | ~40-60% |
| Rule buried in 500+ line file | ~30-50% |
| Generic guideline ("write clean code") | ~0% marginal |

**Source**: Community informal testing, not rigorous benchmarks. Treat as directional.

## The Distributed Repetition Strategy

From the `prompts.ts` source code analysis: Anthropic distributes the same instruction across multiple sections in different wordings. This echoes Google Research's finding (Dec 2025, "Prompt Repetition Improves Non-Reasoning LLMs") that rephrasing activates different attention paths.

**Application**: If you have one critical rule, express it 2-3 times in different contexts:

```markdown
## Rules
- Do not add unrequested features or improvements.

## Testing
- When fixing a bug, only fix the bug. Do not refactor surrounding code.

## Code Review Checklist
- Before committing: verify the diff only contains changes related to the task.
```

Same intent ("don't do extra work"), three different framings, each in a relevant context.

## The Quantified Constraint Strategy

From the ANT internal prompt analysis: Anthropic's own team uses **quantified limits** instead of qualitative ones:

| Qualitative (Lower Compliance) | Quantified (Higher Compliance) |
|--------------------------------|-------------------------------|
| "Be concise" | "≤25 words between tool calls" |
| "Keep functions short" | "Functions ≤40 lines" |
| "Small files" | "200-400 lines typical, 800 max" |
| "Limit dependencies" | "≤3 new packages per PR" |

## The 80/20 of Behavioral CLAUDE.md

If you only do five things:

1. **Add build/test/lint commands** — highest value per line
2. **Add "don't invent, search first"** — prevents hallucination
3. **Add "read before writing"** — prevents blind modifications
4. **Add "don't add unrequested features"** — prevents scope creep
5. **Set up a PostToolUse Hook for formatting** — free 100% compliance

This gets you 80% of the value with 20% of the effort.

## Sources

- Anthropic Official Best Practices — code.claude.com/docs/en/best-practices
- Wisely Chen, "拆解 Claude Code 的 System Prompt 源碼" — ANT internal quantified constraints
- Google Research, "Prompt Repetition Improves Non-Reasoning LLMs" (Dec 2025)
- Jose Parreó García, "How Claude Code Rules Actually Work" (Substack)
- Dev.to: "5 Patterns That Make Claude Code Actually Follow Your Rules"
- Dev.to/Cleverhoods: "CLAUDE.md Best Practices: From Basic to Adaptive"
- HN: "Ask HN: What do you put in claude.md?" (id=44193056)
- HN: "Writing a good Claude.md" (id=46098838)
- abhishekray07/claude-md-templates (GitHub)
- arxiv 2511.09268: "Decoding Configuration of AI Coding Agents"

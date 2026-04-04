# Writing Rules That Stick

Techniques for writing CLAUDE.md rules that Claude actually follows, based on source code analysis and community testing.

## The Question Test

For every rule in your CLAUDE.md, ask:

> "Would Claude make a mistake without this rule?"

If the answer is no, delete the rule. It's wasting instruction budget.

**Source**: Anthropic Official Best Practices, HumanLayer blog

## Rule Sizing

From the source code analysis and community data:

| File Size | Effect |
|-----------|--------|
| 1-80 lines | Optimal. Every rule gets attention. |
| 80-200 lines | Acceptable. Slight compliance drop. |
| 200-500 lines | Noticeable degradation. Consider splitting into `.claude/rules/`. |
| 500+ lines | Significant compliance loss. Claude ignores entire sections. |
| 1000+ lines | Effectively broken. Rules get lost during context compression. |

### Token Budget Reality

Your CLAUDE.md gets ~1,800 tokens in a typical project. The system prompt is 4,200 tokens. You have roughly **30% of the instruction space** that the system prompt has.

Every unnecessary rule dilutes the effective ones. Think of it as a fixed budget: 50 tokens per rule × 36 rules = your full budget. Choose wisely.

## Concrete Over Abstract

The single most consistent finding across all sources:

| Abstract (Low Compliance) | Concrete (High Compliance) |
|---------------------------|---------------------------|
| "Use proper error handling" | "Throw `AppError` from `src/errors.ts`" |
| "Follow the project structure" | "New API routes go in `src/routes/v2/`" |
| "Write good tests" | "Run `pnpm test -- path/to/file.test.ts`" |
| "Keep code clean" | "Functions ≤40 lines. Extract helpers if longer." |
| "Be careful with secrets" | "CRITICAL: Never commit `.env` files." |

**Why**: Concrete rules give Claude a **verifiable action**. Abstract rules require judgment about what "proper" or "good" means, and Claude's judgment may differ from yours.

## The WHAT-WHY Pattern

Rules that explain **why** get better compliance than rules that only state **what**:

```markdown
# Just WHAT (works, but weaker)
- Never modify existing migration files.

# WHAT + WHY (stronger compliance)
- Never modify existing migration files. Migrations are forward-only;
  changing them breaks production databases that already ran the old version.
```

The WHY gives Claude context to apply the rule correctly in edge cases. But keep it to one clause — don't write a paragraph.

## Emphasis Keywords

From source code and community testing:

| Keyword | Effect | Use For |
|---------|--------|---------|
| **CRITICAL** | ~85-90% compliance | Non-negotiable rules (security, data integrity) |
| **IMPORTANT** | ~80-85% compliance | High-priority rules |
| (no keyword) | ~70-80% compliance | Standard rules |

**Constraint**: Use ≤3 emphasized rules per CLAUDE.md. If everything is CRITICAL, the emphasis effect disappears.

## Distributed Repetition

Anthropic's `prompts.ts` spreads the "be concise" instruction across **6 different sections** in different wordings. This is deliberate — Google Research showed that rephrased repetition activates different attention paths.

Apply the same strategy for your most important rules:

```markdown
## Rules
- Do not add features beyond what was requested.

## When Fixing Bugs
- Only fix the reported bug. Do not refactor surrounding code.

## Before Committing
- Verify the diff only contains changes related to the task.
```

Three different contexts, three different phrasings, one core intent: **stay focused**.

## Conditional Blocks

Use `<important if="...">` to scope rules to specific tasks:

```markdown
<important if="modifying database models or migrations">
- Never modify existing migration files. Create new migrations instead.
- Always include a rollback migration.
- Test migrations on a copy of production data first.
</important>

<important if="working on frontend components">
- Use components from src/ui/. Do not create one-off styled components.
- Data fetching through tRPC hooks only. No raw fetch or axios.
</important>
```

These rules only activate when Claude is working in the relevant area, saving attention budget the rest of the time.

## Path-Scoped Rules

For large codebases, use `.claude/rules/` with path frontmatter:

```markdown
<!-- .claude/rules/api-conventions.md -->
---
paths:
  - src/api/**
  - src/routes/**
---

- All endpoints return `{ data, error, meta }` envelope format.
- Validation uses Zod schemas colocated with the route handler.
- Error responses use HTTP status codes from src/errors/httpCodes.ts.
```

These rules **only load when Claude reads files matching the glob pattern**, keeping the base context clean.

## Negative vs Positive Instructions

Community finding from [Dev.to: "5 Patterns That Make Claude Code Actually Follow Your Rules"](https://dev.to/docat0209/5-patterns-that-make-claude-code-actually-follow-your-rules-44dh):

| Negative (Weaker) | Positive (Stronger) |
|-------------------|---------------------|
| "Don't use console.log" | "Use the logger from src/lib/logger.ts" |
| "Don't write long functions" | "Extract functions over 40 lines into helpers" |
| "Don't commit untested code" | "Run `pnpm test` before committing" |

Positive instructions tell Claude **what to do**. Negative instructions leave Claude to figure out the alternative.

**Best**: Combine both: "Use the logger from `src/lib/logger.ts`. Do not use `console.log` in production code."

## HTML Comments Save Tokens

HTML comments are **stripped** before injection into Claude's context:

```markdown
<!-- Note for humans: This rule was added after the Feb 2026 incident -->
- CRITICAL: All user input validated with Zod before processing.
```

The comment is free — it costs zero tokens. Use comments for human-only notes, rationale that's too long for inline, or TODOs.

## Sources

- Anthropic Official Best Practices — code.claude.com/docs/en/best-practices
- Wisely Chen, "拆解 Claude Code 的 System Prompt 源碼" — distributed repetition in prompts.ts
- Anthropic ANT internal prompt — quantified constraints
- Google Research, "Prompt Repetition Improves Non-Reasoning LLMs" (Dec 2025)
- Jose Parreó García, "How Claude Code Rules Actually Work" (Substack)
- Dev.to: "5 Patterns That Make Claude Code Actually Follow Your Rules"
- Dev.to/Cleverhoods: "7 Formatting Rules for the Machine"
- HumanLayer: "Writing a good CLAUDE.md" — humanlayer.dev
- abhishekray07/claude-md-templates — rule templates (GitHub)

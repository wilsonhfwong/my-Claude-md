# Anti-Hallucination Rules

The most requested category of behavioral rules. Claude Code's #1 failure mode is inventing things that don't exist: function signatures, API endpoints, library methods, configuration options.

## The Problem

Without explicit anti-hallucination rules, Claude will:
- Invent function signatures that don't exist in your codebase
- Fabricate third-party API methods based on what "seems right"
- Guess at library interfaces instead of reading documentation
- Assume configuration values, environment variables, or defaults
- Declare bugs "fixed" without verifying the fix works

## The Rules

### Rule 1: Permit Uncertainty

Claude's default behavior is to always provide an answer, even when unsure. You must **explicitly give it permission to say "I don't know."**

```markdown
- If you are unsure about any aspect, say "I don't have enough information
  to confidently do this" instead of guessing.
```

This is Anthropic's own #1 recommendation for reducing hallucination.

**Source**: [Anthropic: Reduce Hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)

### Rule 2: Verify Before Using

```markdown
- Do not invent function signatures, API endpoints, or library methods.
  If you are unsure whether something exists, search the codebase or
  official docs first.
```

**Why it works**: This converts a generation task (make up a plausible API) into a retrieval task (find the actual API). Retrieval is far more reliable.

**Source**: HumanLayer blog, LobeHub anti-hallucination skill, 20+ community reports

### Rule 3: Read Before Writing

```markdown
- Before modifying any file, read it first. Understand the existing code
  before making changes.
```

This is the **single most repeated rule** across all 31 sources. Anthropic's official best practice states: "Explore first, then plan, then code."

Boris Cherny (Claude Code creator): "Spend effort on a solid plan first, then let Claude implement from it."

### Rule 4: Grep Before Assuming

```markdown
- Never hallucinate method chains. Grep for the actual model/class, verify
  constants exist, check relationships, and confirm enums before using them.
```

**Source**: LobeHub anti-hallucination skill decision tree:
- Library signatures → check docs/source
- File content → use Read/Grep tools
- Recent events → use web search
- **Forbidden**: inventing signatures, versions, or citations

### Rule 5: Ask When Information is Missing

```markdown
- If critical information is missing to make a decision, ask me instead
  of proceeding with assumptions.
```

Claude's default is to "helpfully" proceed with its best guess. For anything consequential, this is dangerous. Making it ask is safer.

## Advanced Anti-Hallucination Patterns

### The Spec-Driven Workflow

From [Dev.to: "How I Stopped Claude from Hallucinating on Day 4"](https://dev.to/samhath03/how-i-stopped-claude-code-from-hallucinating-on-day-4-the-spec-driven-workflow-3lim):

```markdown
- Before writing code, read the active spec in .claude/specs/in-progress/.
  Implement exactly what the spec describes. Do not add features not in the spec.
```

By writing requirements in a spec file first, you prevent Claude from guessing at requirements. The spec becomes the source of truth.

### The "Think Before You Code" Pattern

From [Dev.to: "I Made Claude Code Think Before It Codes"](https://dev.to/_vjk/i-made-claude-code-think-before-it-codes-heres-the-prompt-bf):

```markdown
- For any task involving more than 3 files, create a brief plan first:
  1. List the files to modify
  2. Describe the change for each file
  3. Identify risks or dependencies
  Then implement the plan.
```

### Anthropic's Three Official Techniques

From the [Reduce Hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations) docs:

1. **Allow Claude to say "I don't know"** — explicitly permit uncertainty
2. **Require direct quotes** — for factual claims, extract word-for-word quotes from source material
3. **Verify with citations** — have Claude cite sources for each claim, then retract uncitable claims

## Combining with Hooks

Anti-hallucination rules work best at ~85-90% compliance in CLAUDE.md. For the remaining cases, add verification hooks:

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Bash",
      "command": "if echo \"$CLAUDE_TOOL_INPUT\" | grep -qE 'git\\s+commit'; then npm test 2>&1 || (echo 'BLOCKED: Tests must pass before commit' >&2; exit 1); fi"
    }]
  }
}
```

This ensures Claude can't commit code that fails tests, regardless of whether it followed the "run tests" rule.

## What Doesn't Work

- `"Don't hallucinate"` — too vague, no actionable behavior
- `"Be accurate"` — Claude already tries to be; this adds nothing
- `"Double-check your work"` — doesn't specify what "checking" means

What works is **specific, actionable instructions**: search the codebase, read the file, run the tests, ask the user.

## Sources

- Anthropic, Reduce Hallucinations — platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations
- Anthropic Official Best Practices — code.claude.com/docs/en/best-practices
- Boris Cherny (Claude Code Creator) — x.com/bcherny/status/2007179832300581177
- Dev.to: "How I Stopped Claude from Hallucinating" — spec-driven workflow
- Dev.to: "I Made Claude Code Think Before It Codes" — planning pattern
- LobeHub: Anti-Hallucination Skill — lobehub.com/skills/aedelon-claude-code-blueprint-anti-hallucination
- HumanLayer: "Writing a good CLAUDE.md" — humanlayer.dev/blog/writing-a-good-claude-md
- GitHub: assafkip/research-mode — anti-hallucination research mode plugin

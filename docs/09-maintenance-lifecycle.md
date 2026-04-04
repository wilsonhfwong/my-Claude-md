# Maintenance and the Self-Improving Loop

A CLAUDE.md is a living document. The best ones are grown from real mistakes, not written upfront.

## The Self-Improving Loop

From Boris Cherny (Claude Code creator) and the Claude Code team at Anthropic:

```
1. Claude makes a mistake
2. You correct Claude
3. Add a rule to CLAUDE.md so the mistake never happens again
4. Repeat
```

The entire Claude Code team does this. They tag `@.claude` on PR reviews to capture corrections as permanent rules. Every correction becomes a permanent lesson.

**Source**: Boris Cherny on X, Anthropic internal practices

### Automation

You can even ask Claude to do step 3:

> "Update CLAUDE.md so you don't make that mistake again."

Claude will add the rule itself. Review it for accuracy, but this dramatically speeds up the feedback loop.

## The "Start Small, Grow From Pain" Method

**Week 0**: Create a 5-rule CLAUDE.md (use the [Quick Start](01-quick-start.md) template).

**Weeks 1-4**: Use Claude Code normally. When it makes a mistake:
1. Correct it
2. Add a rule
3. Keep going

**Month 1 Review**: You should have 10-20 rules. Ask for each:
- "Did this rule prevent a mistake in the last 30 days?"
- If no → delete it
- If yes → keep it

**Quarterly**: Review the whole file. Merge duplicate rules. Remove rules for mistakes Claude no longer makes (model improvements may have fixed them).

This approach consistently produces better CLAUDE.md files than writing 50 rules upfront, because every rule addresses a real problem you actually experienced.

## Weekly Quick Check (5 minutes)

```
□ Did Claude violate any rules this week? → Add rules for new violations
□ Any rules feel redundant? → Delete them
□ File under 80 lines? → If not, consider pruning or splitting
```

## Monthly Review (30 minutes)

```
□ For each rule: "Did this prevent a mistake in the last 30 days?"
  → No? Delete it
□ Check for contradictions between rules
□ Move pure formatting rules to Hooks (if not already)
□ Move "never do X" rules to Hooks (if not already)
□ Update build/test/lint commands if they changed
```

## Quarterly Deep Review (1 hour)

```
□ Read the full CLAUDE.md — does it still reflect how you actually work?
□ Are there rules about old patterns/frameworks you've moved away from?
□ Test with a fresh Claude session: does it follow the rules on first try?
□ Compare with team members' local overrides — any good rules to promote?
□ Check if Claude model updates have fixed issues rules were working around
```

## Team Workflow

For teams, CLAUDE.md is shared infrastructure:

### PR Reviews
When reviewing PRs where Claude made mistakes:
1. Comment on the PR noting the mistake
2. Add a CLAUDE.md rule in the same PR (or a follow-up)
3. The rule ships with the fix

### Ownership
Assign CLAUDE.md to the team lead or a rotating owner:
- Reviews CLAUDE.md changes in PRs
- Runs monthly pruning
- Resolves conflicting rules

### Local Overrides
Individual developers use `CLAUDE.local.md` (gitignored) for personal preferences:

```markdown
<!-- CLAUDE.local.md -->
- I prefer functional style over class-based.
- When writing tests, include edge cases for null/undefined inputs.
- Always explain your reasoning before making changes.
```

These don't affect teammates.

## Context Window Hygiene

From community observations:
- At **50% context** → consider running `/compact`
- At **70% context** → precision drops noticeably
- At **85% context** → hallucinations increase
- At **90%+ context** → responses become erratic

CLAUDE.md survives compaction (re-read from disk). Conversation-only instructions don't. If something matters, it must be in CLAUDE.md.

### The `/clear` Strategy

For long sessions:
1. Complete a logical unit of work
2. Run `/clear` to reset context
3. Claude re-reads CLAUDE.md fresh
4. Start the next task with full context budget

This prevents rule compliance degradation that happens as context fills up.

## Anti-Patterns

### The Dumping Ground
Adding every observation to CLAUDE.md without pruning. File grows to 500+ lines, compliance drops across the board.

**Fix**: Monthly pruning. Apply the Question Test to every rule.

### The Write-Once File
Creating CLAUDE.md at project start and never updating it.

**Fix**: The self-improving loop. Treat it as code that needs maintenance.

### Copy-Pasting from the Internet
Taking someone else's CLAUDE.md wholesale without adapting it.

**Fix**: Start with 5 rules from your own experience. Add from templates only if they address problems you've actually had.

### Rules About Rules
Meta-instructions like "Always follow these rules" or "These rules are mandatory."

**Fix**: Delete them. Claude already knows CLAUDE.md contains rules. Meta-instructions waste tokens.

## Sources

- Boris Cherny (Claude Code Creator) — self-improving loop, team workflow
- Anthropic Official Best Practices — start small, grow incrementally
- Anthropic Memory Documentation — compaction behavior, file size recommendations
- HN: "Ask HN: What do you put in claude.md?" — community maintenance patterns
- Dev.to/Cleverhoods: "From Basic to Adaptive" — maturity levels
- Community observations — context window degradation thresholds

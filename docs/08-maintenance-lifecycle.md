# Maintenance Lifecycle

A CLAUDE.md that isn't maintained decays. Rules become stale, the file grows, and compliance drops. This guide covers how to keep your CLAUDE.md effective over time.

## The Growth Curve

### Week 1: Bootstrap

Start with 5 rules. That's it.

Pick them by working with Claude Code for a few sessions without any CLAUDE.md. Note every time you correct Claude. Your top 5 corrections become your first rules.

Also add your build/test/lint commands -- these are nearly always high value.

### Weeks 2-8: Incremental Growth

Add **one rule per week** when you catch a recurring mistake. This forces prioritization -- you can only add the most important one.

Before adding, apply the Question Test: "Would Claude make a mistake without this?" If the answer is "maybe once," wait and see if it recurs.

### Monthly Audit

Once a month, read every rule. For each one, ask:

1. **"Did this rule prevent a mistake in the last 30 days?"** -- If not, delete it.
2. **"Does Claude follow this without the rule?"** -- If yes, delete it (Claude may have learned it from your codebase).
3. **"Is this better as a Hook?"** -- If it's mechanical (formatting, linting), move it.
4. **"Is this still accurate?"** -- Stale rules (referencing deleted files, old patterns) actively mislead.

Expect to delete 10-20% of rules each month. This is healthy.

### Quarterly Review

Every 3 months, do a deeper review:

- Has the tech stack changed? Update commands and tool references.
- Have architectural patterns evolved? Update structural rules.
- Are there new team members with different conventions? Reconcile.
- Has Claude Code been updated? Some rules may no longer be necessary.

## Team Process

### CLAUDE.md as Code

Treat CLAUDE.md changes like any other code change:

- **Version control**: CLAUDE.md is committed to git (project level)
- **Code review**: PRs that modify CLAUDE.md get reviewed like code changes
- **Descriptive commits**: `git commit -m "Add rule for API envelope format after repeated mistakes"`
- **git blame**: Use it to understand why rules were added

### Shared Ownership

Patterns that work for teams:

- **Tag coworkers** on PRs that update CLAUDE.md -- build shared understanding
- **Rotate review**: Different team members audit CLAUDE.md each month
- **Post-incident updates**: After a bug caused by Claude, add (or fix) the relevant rule
- **Onboarding**: New team members review CLAUDE.md as part of onboarding

### Resolving Disagreements

When team members disagree about a rule:

1. Check if it's a personal preference -> move to `~/.claude/CLAUDE.md` (user level)
2. Check if it's enforceable mechanically -> move to a Hook (removes subjectivity)
3. If it's genuinely a team decision -> discuss, decide, document the decision in the commit message

## Measuring Effectiveness

### Direct Signals

- **Correction frequency**: Track how often you correct Claude on things covered by rules. Decreasing = rules are working. Persistent = rules need rewriting.
- **Rule hit rate**: During monthly audit, mark which rules actually triggered. Rules that never activate should be questioned.

### Indirect Signals

- **Session productivity**: Are you completing tasks faster with your current CLAUDE.md?
- **Context window usage**: Are you hitting context limits earlier? Your CLAUDE.md might be too large.
- **Cost per session**: Increasing costs may indicate cache invalidation or context bloat.

### Anti-Metrics

Don't optimize for:

- **Number of rules** -- more isn't better
- **File length** -- shorter isn't always better if you're cutting valuable rules
- **Coverage** -- you don't need a rule for every possible situation

## Common Lifecycle Mistakes

### 1. Never Updating

The most common failure mode. A CLAUDE.md written 6 months ago for a different version of the codebase actively misleads Claude.

**Fix**: Set a monthly calendar reminder. Spend 10 minutes reviewing.

### 2. Only Adding, Never Removing

Files grow monotonically. Every rule seems important when you add it, but importance changes over time.

**Fix**: For every rule you add, try to remove one. Maintain a budget mentality.

### 3. Updating After Every Minor Issue

Over-reacting to one-off mistakes creates bloated, micro-managing CLAUDE.md files. Not every mistake needs a rule.

**Fix**: Wait for a mistake to recur 3 times before adding a rule. One-off errors are noise.

### 4. Ignoring Stale References

Rules that reference deleted files, renamed functions, or deprecated patterns cause confusion. Claude may follow the outdated instruction faithfully, producing code that doesn't match the current codebase.

**Fix**: When you refactor, search CLAUDE.md for affected file paths and patterns. Update or delete.

### 5. Separate Team Member Files Without Coordination

Multiple team members maintaining their own `~/.claude/CLAUDE.md` with conflicting rules creates inconsistent Claude behavior across the team.

**Fix**: Personal preferences go in `~/.claude/CLAUDE.md`. Team standards go in `./CLAUDE.md`. The project level wins on conflicts.

## A Maintenance Checklist

Use this during monthly reviews:

```
[ ] Read every rule. Does each one pass the Question Test?
[ ] Delete rules Claude now follows without instruction.
[ ] Delete rules that reference deleted/renamed code.
[ ] Move mechanical rules (formatting, linting) to Hooks.
[ ] Check for contradictions between rules.
[ ] Verify commands still work (build, test, lint).
[ ] Check file size: still under 200 lines?
[ ] Count actionable rules: still under 100?
[ ] Update any outdated file paths or patterns.
[ ] Commit changes with descriptive message.
```

## The Lifecycle in Summary

```
Week 1:     5 rules from real corrections + build/test commands
Weeks 2-8:  +1 rule per week for recurring mistakes
Monthly:    Audit: delete stale, move mechanical, verify accuracy
Quarterly:  Deep review: tech stack, architecture, team alignment
Ongoing:    Post-incident: add/fix rules after Claude-caused bugs
```

The goal is not a perfect CLAUDE.md. The goal is a CLAUDE.md that reflects your current project, addresses your current pain points, and stays lean enough to fit within your instruction budget.

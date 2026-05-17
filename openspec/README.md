# OpenSpec

This directory contains [OpenSpec](https://openspec.dev) change proposals — the
PRDs and capability specs that drive implementation of new features in this
repository.

## Layout

```
openspec/
  changes/
    <change-id>/
      proposal.md      Why, what changes, impact
      tasks.md         Implementation checklist
      design.md        Decisions, risks, open questions
      specs/
        <capability>/spec.md   Requirements + WHEN/THEN scenarios
```

## Active changes

- [`add-quarterly-earnings-summarizer`](./changes/add-quarterly-earnings-summarizer/proposal.md)
  — greenfield Python web app that ingests 8-K, 10-Q/10-K, IR decks and earnings
  call audio per ticker+quarter, produces a structured five-section summary with
  a cited directional signal, and continuously improves itself through an
  agent-driven evaluation feedback loop.

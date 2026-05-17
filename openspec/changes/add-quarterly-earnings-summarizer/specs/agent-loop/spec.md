# Agent Loop Capability

## ADDED Requirements

### Requirement: One iteration SHALL be invocable as a standalone script
The system SHALL provide `python -m agent.loop` that runs one iteration using
the Anthropic Agent SDK and exits.

#### Scenario: Cron-driven invocation
- **WHEN** cron invokes the script
- **THEN** exactly one iteration runs and the process exits 0 on success

### Requirement: The agent SHALL propose prompt variants targeting worst failures
Each iteration SHALL read the latest eval report, identify the worst-scoring
dimension and items, and propose 1-3 prompt variants targeting those failures.

#### Scenario: Targeted variants
- **WHEN** the worst dimension in the latest report is `faithfulness`
- **THEN** the proposed variants SHALL include explicit faithfulness guidance
- **AND** each variant SHALL include a written hypothesis in `notes`

### Requirement: Stop criteria SHALL be enforced
The loop SHALL stop and exit non-fatally when any of: (a) no accepted variant in
the last 5 iterations, (b) 50 iterations have occurred for the task this week,
(c) cumulative cost exceeds the configured cap, (d) all judge dimensions are at
or above their target thresholds.

#### Scenario: Plateau detection
- **WHEN** the last 5 iterations were all `reject`
- **THEN** the loop exits with status `plateau`

#### Scenario: Cost cap reached
- **WHEN** projected next-iteration cost would exceed the cap
- **THEN** the loop refuses to start the iteration
- **AND** exits with status `cost_cap_reached`

### Requirement: The agent SHALL NOT modify the judge prompt
In v1, the agent loop SHALL NOT write to `prompts/judge/**`.

#### Scenario: Judge prompt is off-limits
- **WHEN** the agent attempts to write a judge prompt file
- **THEN** the registry rejects the write
- **AND** records `decision = 'reject'` with rationale `judge_locked_v1`

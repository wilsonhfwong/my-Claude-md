# Evaluation Capability

## ADDED Requirements

### Requirement: Eval runs SHALL be executable via a single CLI
The system SHALL provide `python -m eval.run --prompt <id> --model <id>
--gold-set <version>` that runs an eval and writes
`eval/reports/<run_id>.json` and `eval/reports/<run_id>.md`.

#### Scenario: Successful eval run
- **WHEN** the CLI is invoked with valid arguments
- **THEN** both report files are written
- **AND** `eval_runs.status` is `succeeded`

### Requirement: Three scorers SHALL run on every eval item
Every gold item SHALL be scored by all of: a **deterministic** scorer, a
**reference-based** scorer, and an **LLM-as-judge** scorer.

#### Scenario: Deterministic scorer rejects rounded EPS
- **WHEN** the LLM emits EPS as `1.7` for an item whose ground truth is `1.65`
- **THEN** the deterministic scorer marks the item failed
- **AND** the failure appears in the report's "top failures" table

#### Scenario: Judge scorer scores faithfulness
- **WHEN** the judge prompt is run on an item
- **THEN** it emits Likert scores (1-5) for faithfulness, completeness,
  brevity, and calibration

### Requirement: Aggregated scores SHALL include 95% bootstrap CIs
Aggregated scores in the report SHALL include the mean and a 95% confidence
interval from 1000 bootstrap resamples.

#### Scenario: CI overlap blocks promotion
- **WHEN** a candidate prompt's mean is higher than the incumbent's but the 95%
  CIs overlap
- **THEN** the agent loop SHALL NOT promote the candidate

### Requirement: Champion promotion SHALL require statistical significance
A candidate (prompt_id, model) SHALL only become champion when its mean exceeds
the incumbent's at p < 0.05 with non-overlapping 95% CIs.

#### Scenario: Significant improvement
- **WHEN** a candidate beats the incumbent at p < 0.05 with non-overlapping CIs
- **THEN** the agent loop updates `index.yaml`
- **AND** writes an `agent_iterations` row with `decision = 'accept'`

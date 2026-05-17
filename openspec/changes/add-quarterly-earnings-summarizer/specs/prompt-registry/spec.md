# Prompt Registry Capability

## ADDED Requirements

### Requirement: Prompts SHALL be versioned, append-only YAML files
Prompts live in `/prompts/<task>/<name>.v<N>.yaml`; once a file exists at a given
`(task, name, version)` it SHALL NOT be modified.

#### Scenario: Adding a new version
- **WHEN** the agent proposes a variant of `summary.metrics.v3`
- **THEN** it writes `summary.metrics.v4.yaml`
- **AND** does not modify `summary.metrics.v3.yaml`

### Requirement: A champion pointer SHALL select the current version per task
Each task directory SHALL contain `index.yaml` naming the champion version; this
file is the only mutable artifact in the registry.

#### Scenario: Champion promotion
- **WHEN** the agent loop accepts a new version
- **THEN** it updates `index.yaml` to point at the new version
- **AND** records the change in `agent_iterations`

### Requirement: Prompt files SHALL be lintable
A CI lint step SHALL parse every prompt file, reject unknown fields, and
require that `output_schema` resolves to a real JSON schema.

#### Scenario: Lint catches malformed prompt
- **WHEN** a prompt file contains an unknown field `foobar`
- **THEN** the lint step exits non-zero
- **AND** CI fails the change

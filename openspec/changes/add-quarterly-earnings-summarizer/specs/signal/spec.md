# Signal Capability

## ADDED Requirements

### Requirement: The signal SHALL be one of three labels with confidence and evidence
The signal output SHALL be `{bullish, neutral, bearish}` with a confidence value
in `[0, 1]` and at least one evidence item pointing to an artifact (filing id or
transcript segment id).

#### Scenario: Bullish signal with evidence
- **WHEN** the signal classifier outputs `bullish` with confidence 0.72
- **THEN** the JSON SHALL contain at least one evidence item
- **AND** each evidence item references an existing artifact id

#### Scenario: Reject signal without evidence
- **WHEN** the LLM emits a signal with no evidence array
- **THEN** schema validation fails
- **AND** the summary is retried per the summarization retry policy

### Requirement: The disclaimer SHALL be wrapper-injected and non-removable
The signal envelope SHALL include the exact string
`"Informational only, not investment advice."` in a `disclaimer` field; this
field is set by the application wrapper and SHALL NOT be removable or alterable
by the LLM.

#### Scenario: Disclaimer present on every signal
- **WHEN** any summary with a signal is read from storage
- **THEN** `signal.disclaimer` equals the canonical disclaimer string

#### Scenario: Disclaimer rendered in UI
- **WHEN** any page rendering a signal is served
- **THEN** the disclaimer text SHALL be visible without user interaction

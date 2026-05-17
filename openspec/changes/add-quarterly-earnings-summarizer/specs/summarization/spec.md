# Summarization Capability

## ADDED Requirements

### Requirement: The summary output SHALL be structured into five sections
The system SHALL emit JSON with top-level keys `metrics`, `narrative`,
`guidance_qa`, `sentiment`, and `signal`; the output SHALL validate against the
schemas under `app/summarize/schemas/`.

#### Scenario: Valid summary produced
- **WHEN** the pipeline runs end-to-end for a (ticker, period)
- **THEN** the output JSON contains all five keys
- **AND** validates against the JSON schemas

#### Scenario: Invalid LLM output is retried
- **WHEN** the LLM emits a payload that fails schema validation
- **THEN** the wrapper retries up to 2 times with a tightened repair prompt
- **AND** marks the summary as `failed` after the final retry

### Requirement: Every metric SHALL carry a source citation
Each item in `metrics` SHALL include `source_filing_id` and one of
`{xbrl_fact_id, page_offset, quote}` referencing the originating artifact.

#### Scenario: EPS extraction with citation
- **WHEN** EPS is extracted for AAPL FY2025 Q2
- **THEN** the `metrics.eps` item references the 8-K filing id
- **AND** the value matches the EDGAR XBRL fact to the cent

### Requirement: Q&A quotes SHALL be verbatim
Every quoted line in `guidance_qa` SHALL be a substring of the transcript text
(normalized for whitespace and case).

#### Scenario: Quote substring check
- **WHEN** the deterministic scorer runs
- **THEN** each cited quote SHALL be found as a substring in the transcript
- **AND** any mismatch fails the deterministic scorer

### Requirement: Sentiment SHALL include a quarter-over-quarter delta
The `sentiment` section SHALL report current-quarter tone and a delta vs the
immediately prior quarter, requiring retrieval over historical transcripts.

#### Scenario: First-quarter coverage of a company
- **WHEN** no prior quarter exists in the database
- **THEN** the delta field is `null`
- **AND** the UI renders "no prior quarter available"

# Web UI Capability

## ADDED Requirements

### Requirement: The UI SHALL provide pages for companies, summaries, evals, and the agent
The system SHALL render pages for: company list, company detail, summary detail
(five-card view), evaluation report viewer, leaderboard, agent run history.

#### Scenario: Browsing a summary
- **WHEN** a user navigates to a summary detail page
- **THEN** the five sections are rendered as separate cards
- **AND** a raw-JSON toggle reveals the unredacted output schema instance

### Requirement: The disclaimer SHALL be visible wherever a signal appears
Every page that displays a signal SHALL render the canonical disclaimer
prominently without requiring user interaction.

#### Scenario: Disclaimer visible on summary detail
- **WHEN** the summary detail page renders a signal
- **THEN** the disclaimer text is visible above or adjacent to the signal label

### Requirement: Triggering ingestion SHALL be non-blocking
Triggering an ingestion or summarization SHALL enqueue a job and return a job id
synchronously; status SHALL be observable on a job-status page.

#### Scenario: Job submission
- **WHEN** a user triggers ingestion for a (ticker, period)
- **THEN** the response includes a `job_id`
- **AND** the job-status page polls until completion

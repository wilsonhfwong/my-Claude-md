# Ingestion Capability

## ADDED Requirements

### Requirement: The system SHALL fetch SEC filings by ticker and fiscal period
The system SHALL fetch 8-K, 10-Q, and 10-K filings for a given (ticker, fiscal
year, fiscal quarter) tuple from SEC EDGAR using a compliant User-Agent and a
token-bucket rate limiter capped at 8 requests per second.

#### Scenario: Successful fetch of a 10-Q
- **WHEN** a user requests ingestion for `AAPL` FY2025 Q2
- **THEN** the system fetches the 8-K, 10-Q, and any 10-K from EDGAR
- **AND** persists each blob with its SHA-256 and source URL
- **AND** sets the filing's `fetched_at` timestamp

#### Scenario: Idempotent re-fetch
- **WHEN** the same (ticker, period, kind) is requested twice
- **THEN** the second call returns the existing record
- **AND** does not create a duplicate blob

#### Scenario: Rate-limit compliance
- **WHEN** the system makes EDGAR requests
- **THEN** the global request rate SHALL NOT exceed 8 requests per second
- **AND** the User-Agent header SHALL include an identifying contact email

### Requirement: The system SHALL fetch earnings call audio and IR decks
The system SHALL fetch archived earnings call audio and (when available) the
investor presentation slide deck for a given (ticker, period) via a configured
`EarningsAudioProvider`.

#### Scenario: Audio and deck available
- **WHEN** the provider has audio and a deck for the period
- **THEN** both blobs are persisted with SHA-256
- **AND** `filings.kind` is `DECK` for the deck and `transcripts.audio_blob_path`
  is set for the audio

#### Scenario: Deck missing
- **WHEN** the provider has audio but no deck
- **THEN** ingestion succeeds with `deck` absent
- **AND** the UI exposes a manual upload affordance

### Requirement: The system SHALL accept manual deck uploads
The system SHALL allow a user to upload a presentation deck PDF; uploaded files
SHALL have their metadata stripped on ingest.

#### Scenario: User uploads a deck
- **WHEN** a user uploads `acme_q2_2025.pdf`
- **THEN** the system writes a metadata-scrubbed copy to blob storage
- **AND** records a `filings` row with `source = 'upload'`

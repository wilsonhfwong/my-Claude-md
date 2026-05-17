# Storage Capability

## ADDED Requirements

### Requirement: The schema SHALL be Postgres-portable
All tables SHALL use UUIDv7 TEXT primary keys, ISO-8601 UTC timestamps, and no
SQLite-only types; an Alembic `upgrade head` SHALL succeed against a fresh
Postgres database.

#### Scenario: Postgres dry-run
- **WHEN** `alembic upgrade head` runs against an empty Postgres container
- **THEN** all migrations apply cleanly
- **AND** the resulting schema matches the SQLite schema modulo dialect

### Requirement: Blob storage SHALL be adapter-based
Blob reads and writes SHALL go through a `BlobStore` Protocol; v1 implements
`LocalBlobStore`, Phase 2 implements `S3BlobStore`.

#### Scenario: Adapter swap by config
- **WHEN** the configured blob backend is changed from `local` to `s3`
- **THEN** subsequent reads and writes use S3 without code changes

### Requirement: Re-ingestion SHALL be idempotent
Ingesting the same (ticker, period, kind) tuple twice SHALL NOT produce
duplicate `filings` or `transcripts` rows.

#### Scenario: Repeat ingestion
- **WHEN** ingestion runs twice for `AAPL` FY2025 Q2
- **THEN** the count of `filings` rows for that tuple is unchanged after the
  second run

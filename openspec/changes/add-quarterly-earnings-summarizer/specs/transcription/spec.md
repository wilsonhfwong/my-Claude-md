# Transcription Capability

## ADDED Requirements

### Requirement: The system SHALL produce a batch transcript with time-coded segments
The system SHALL transcribe a downloaded earnings call audio file in batch using
`faster-whisper`, producing time-coded segments (start, end, text, optional
speaker) persisted as `transcripts.segments_json`.

#### Scenario: Batch transcription completes
- **WHEN** an audio blob is available for a (ticker, period)
- **THEN** the worker produces a transcript with at least one segment per
  contiguous speech region
- **AND** records `mode = 'batch'`, `model`, `duration_s`, and `language`

### Requirement: Transcription quality SHALL be validated on the anchor case
On the AAPL FY2025 Q2 anchor, the word error rate measured on 10 random
30-second clips against the Quartr transcript SHALL NOT exceed 8%.

#### Scenario: WER spot-check on the anchor
- **WHEN** the verification suite runs `tools/wer_spot_check.py`
- **THEN** the reported mean WER SHALL be less than or equal to 0.08
- **AND** CI fails if it is greater

### Requirement: Phase 2 SHALL support streaming transcription
[Phase 2] The system SHALL support real-time streaming transcription via Deepgram
and SHALL push incremental summary updates to the browser over SSE.

#### Scenario: Live call streaming (Phase 2)
- **WHEN** a configured live call begins
- **THEN** the system opens a Deepgram stream
- **AND** emits incremental transcript segments to subscribed SSE clients
- **AND** triggers section-level re-summarization at most once per 30 seconds

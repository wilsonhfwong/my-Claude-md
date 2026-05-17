# LLM Router Capability

## ADDED Requirements

### Requirement: All LLM calls SHALL go through one provider abstraction
The system SHALL expose a single `complete(prompt_id, inputs, model) ->
Completion` API backed by LiteLLM and SHALL support Anthropic, OpenAI, Google,
and Ollama providers.

#### Scenario: Switching providers by config
- **WHEN** the configured default model is changed from
  `anthropic/claude-sonnet-4-6` to `openai/gpt-4.1`
- **THEN** subsequent calls route to OpenAI without code changes

### Requirement: Every call SHALL record cost and latency
Each `Completion` SHALL persist `prompt_id`, `prompt_version`, `model`,
`tokens_in`, `tokens_out`, `cost_usd`, and `latency_ms`.

#### Scenario: Cost accounting
- **WHEN** a summarization call completes
- **THEN** a row is appended that includes a non-null `cost_usd`
- **AND** the value is computed from the provider's published pricing

### Requirement: Logs SHALL NOT contain raw prompts or API keys at default level
At the default log level, prompt bodies and any secret-looking token
(`sk-…`, `AIza…`, Bearer tokens) SHALL be redacted.

#### Scenario: Redaction in logs
- **WHEN** a call is logged at INFO
- **THEN** the log line contains `prompt_id` and `tokens_*` but not the prompt
  body
- **AND** any matching secret pattern is replaced with `***`

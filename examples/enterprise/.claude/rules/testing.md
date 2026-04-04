<important if="writing, modifying, or reviewing tests">

## Test Requirements

### Go Services
- Table-driven tests for all public functions.
- Use `testify/assert` and `testify/require`, not raw `if` checks.
- Mock external services with interfaces. Mocks live in `<package>/mocks/`.
- Integration tests use `testcontainers-go` for database dependencies.
- Test files: `<name>_test.go` in the same package.

### Frontend
- Components tested with `@testing-library/react`.
- API integration tests use MSW (Mock Service Worker).
- E2E tests in `frontend/e2e/` use Playwright.
- Minimum coverage: 80% for new code (enforced in CI).

### General
- Every PR must include tests for new functionality.
- Test names describe the scenario: `Test_CreateUser_WithDuplicateEmail_ReturnsConflict`.
- No test should depend on execution order or shared mutable state.
- Tests must pass in CI without network access to external services.

</important>

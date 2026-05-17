import logging

from app.observability.logging import SecretRedactor


def _make_record(msg: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="t", level=logging.INFO, pathname="", lineno=0, msg=msg, args=(), exc_info=None
    )


def test_redacts_openai_key() -> None:
    record = _make_record("api_key=sk-abcdefghijklmnopqrstuvwxyz tail")
    SecretRedactor().filter(record)
    redacted = record.getMessage()
    assert "***" in redacted
    assert "sk-abc" not in redacted


def test_redacts_google_key() -> None:
    record = _make_record("token=AIzaSyAabcdefghijklmnop12345 tail")
    SecretRedactor().filter(record)
    redacted = record.getMessage()
    assert "***" in redacted
    assert "AIzaSy" not in redacted


def test_redacts_bearer_token() -> None:
    record = _make_record("Authorization: Bearer abcdefghijklmnop1234567890")
    SecretRedactor().filter(record)
    redacted = record.getMessage()
    assert "***" in redacted
    assert "Bearer abcd" not in redacted


def test_leaves_safe_strings_alone() -> None:
    record = _make_record("user=alice action=login result=ok")
    SecretRedactor().filter(record)
    assert record.getMessage() == "user=alice action=login result=ok"

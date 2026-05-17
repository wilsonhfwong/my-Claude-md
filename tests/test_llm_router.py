from pathlib import Path

import pytest

from app.llm import FakeLLMResponse, FakeLLMRouter, PromptRegistry


@pytest.fixture
def registry(tmp_path: Path) -> PromptRegistry:
    (tmp_path / "summarize").mkdir()
    (tmp_path / "summarize" / "v1.toml").write_text(
        'model = "anthropic/claude-sonnet-4-6"\n'
        "max_tokens = 512\n"
        'system = "You summarize."\n'
        'user_template = "Summarize: {{ text }}"\n'
    )
    return PromptRegistry(root=tmp_path)


def test_fake_router_returns_default_response(registry: PromptRegistry) -> None:
    router = FakeLLMRouter(registry, default_response=FakeLLMResponse(text="ok"))
    result = router.run("summarize", 1, {"text": "hello"})
    assert result.text == "ok"
    assert result.prompt_id == "summarize:v1"
    assert result.model == "anthropic/claude-sonnet-4-6"
    assert result.usage.total_tokens == result.usage.input_tokens + result.usage.output_tokens


def test_fake_router_returns_configured_response(registry: PromptRegistry) -> None:
    router = FakeLLMRouter(registry)
    router.set_response("summarize", "the summary text")
    result = router.run("summarize", 1, {"text": "hello"})
    assert result.text == "the summary text"


def test_fake_router_records_rendered_prompt(registry: PromptRegistry) -> None:
    router = FakeLLMRouter(registry)
    router.run("summarize", 1, {"text": "hello world"})
    assert len(router.calls) == 1
    call = router.calls[0]
    assert call["prompt_id"] == "summarize:v1"
    assert call["rendered_user"] == "Summarize: hello world"
    assert call["system"] == "You summarize."
    assert call["model"] == "anthropic/claude-sonnet-4-6"


def test_fake_router_honours_model_override(registry: PromptRegistry) -> None:
    router = FakeLLMRouter(registry)
    result = router.run("summarize", 1, {"text": "x"}, model_override="openai/gpt-4o-mini")
    assert result.model == "openai/gpt-4o-mini"
    assert router.calls[0]["model"] == "openai/gpt-4o-mini"


def test_fake_router_request_id_is_unique_per_call(registry: PromptRegistry) -> None:
    router = FakeLLMRouter(registry)
    ids = {router.run("summarize", 1, {"text": str(i)}).request_id for i in range(3)}
    assert len(ids) == 3

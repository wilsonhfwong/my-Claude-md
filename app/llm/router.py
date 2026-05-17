from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Protocol

from app.llm.prompts import PromptRegistry

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int
    output_tokens: int
    total_tokens: int


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str
    prompt_id: str
    request_id: str
    latency_ms: int
    usage: LLMUsage


class LLMRouter(Protocol):
    def run(
        self,
        prompt_name: str,
        version: int,
        variables: dict[str, object],
        *,
        model_override: str | None = None,
    ) -> LLMResult: ...


class LiteLLMRouter:
    """Dispatches LLM calls through litellm so the same code path can target
    Anthropic, OpenAI, Google, etc. based on the `model` string in each prompt
    config (e.g. "anthropic/claude-sonnet-4-6", "openai/gpt-4o-mini").

    Provider-specific features (Anthropic prompt-cache breakpoints, adaptive
    thinking) are not exposed here. Add them as prompt config fields and
    forward via `extra_body` when needed.
    """

    def __init__(self, registry: PromptRegistry) -> None:
        self.registry = registry

    def run(
        self,
        prompt_name: str,
        version: int,
        variables: dict[str, object],
        *,
        model_override: str | None = None,
    ) -> LLMResult:
        import litellm

        prompt = self.registry.get(prompt_name, version)
        user_text = self.registry.render(prompt, variables)
        model = model_override or prompt.model

        kwargs: dict[str, object] = {
            "model": model,
            "max_tokens": prompt.max_tokens,
            "messages": [
                {"role": "system", "content": prompt.system},
                {"role": "user", "content": user_text},
            ],
        }
        if prompt.temperature is not None:
            kwargs["temperature"] = prompt.temperature

        start = time.monotonic()
        response = litellm.completion(**kwargs)
        latency_ms = int((time.monotonic() - start) * 1000)

        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)
        result = LLMResult(
            text=text,
            model=model,
            prompt_id=prompt.id,
            request_id=getattr(response, "id", "") or "",
            latency_ms=latency_ms,
            usage=LLMUsage(
                input_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                output_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
                total_tokens=int(getattr(usage, "total_tokens", 0) or 0),
            ),
        )
        log.info(
            "llm_call prompt=%s model=%s latency_ms=%d tokens_in=%d tokens_out=%d",
            result.prompt_id,
            result.model,
            result.latency_ms,
            result.usage.input_tokens,
            result.usage.output_tokens,
        )
        return result


@dataclass
class FakeLLMResponse:
    text: str
    input_tokens: int = 100
    output_tokens: int = 50


class FakeLLMRouter:
    """In-memory router for tests. Records every call so assertions can
    inspect the rendered prompt without hitting the network.
    """

    def __init__(
        self,
        registry: PromptRegistry,
        responses: dict[str, FakeLLMResponse] | None = None,
        default_response: FakeLLMResponse | None = None,
    ) -> None:
        self.registry = registry
        self.responses = responses or {}
        self.default_response = default_response or FakeLLMResponse(text="(fake)")
        self.calls: list[dict[str, object]] = []

    def set_response(self, prompt_name: str, response: FakeLLMResponse | str) -> None:
        if isinstance(response, str):
            response = FakeLLMResponse(text=response)
        self.responses[prompt_name] = response

    def run(
        self,
        prompt_name: str,
        version: int,
        variables: dict[str, object],
        *,
        model_override: str | None = None,
    ) -> LLMResult:
        prompt = self.registry.get(prompt_name, version)
        rendered = self.registry.render(prompt, variables)
        canned = self.responses.get(prompt_name, self.default_response)
        self.calls.append(
            {
                "prompt_id": prompt.id,
                "rendered_user": rendered,
                "system": prompt.system,
                "model": model_override or prompt.model,
                "variables": variables,
            }
        )
        return LLMResult(
            text=canned.text,
            model=model_override or prompt.model,
            prompt_id=prompt.id,
            request_id=f"fake-{len(self.calls):04d}",
            latency_ms=0,
            usage=LLMUsage(
                input_tokens=canned.input_tokens,
                output_tokens=canned.output_tokens,
                total_tokens=canned.input_tokens + canned.output_tokens,
            ),
        )

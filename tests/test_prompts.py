from pathlib import Path

import pytest

from app.llm.prompts import Prompt, PromptRegistry


@pytest.fixture
def registry(tmp_path: Path) -> PromptRegistry:
    (tmp_path / "greet").mkdir()
    (tmp_path / "greet" / "v1.toml").write_text(
        'model = "anthropic/claude-haiku-4-5"\n'
        "max_tokens = 256\n"
        'system = "You are friendly."\n'
        'user_template = "Hello, {{ name }}!"\n'
    )
    (tmp_path / "greet" / "v2.toml").write_text(
        'model = "anthropic/claude-sonnet-4-6"\n'
        "max_tokens = 512\n"
        "temperature = 0.7\n"
        'system = "You are warm and effusive."\n'
        'user_template = "Hello, {{ name }}!"\n'
    )
    return PromptRegistry(root=tmp_path)


def test_get_loads_and_validates(registry: PromptRegistry) -> None:
    p = registry.get("greet", 1)
    assert p.name == "greet"
    assert p.version == 1
    assert p.id == "greet:v1"
    assert p.model == "anthropic/claude-haiku-4-5"
    assert p.max_tokens == 256
    assert p.temperature is None
    assert p.system == "You are friendly."


def test_get_caches_repeated_loads(registry: PromptRegistry) -> None:
    assert registry.get("greet", 1) is registry.get("greet", 1)


def test_missing_prompt_raises(registry: PromptRegistry) -> None:
    with pytest.raises(FileNotFoundError):
        registry.get("nonexistent", 1)


def test_missing_version_raises(registry: PromptRegistry) -> None:
    with pytest.raises(FileNotFoundError):
        registry.get("greet", 99)


def test_required_keys_validated(tmp_path: Path) -> None:
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "v1.toml").write_text(
        'model = "anthropic/claude-sonnet-4-6"\nsystem = "x"\n'
    )
    reg = PromptRegistry(root=tmp_path)
    with pytest.raises(ValueError, match="missing keys"):
        reg.get("bad", 1)


def test_render_substitutes_variables(registry: PromptRegistry) -> None:
    p = registry.get("greet", 1)
    assert registry.render(p, {"name": "Alice"}) == "Hello, Alice!"


def test_render_undefined_variable_raises(registry: PromptRegistry) -> None:
    from jinja2 import UndefinedError

    p = registry.get("greet", 1)
    with pytest.raises(UndefinedError):
        registry.render(p, {})


def test_list_versions_sorted(registry: PromptRegistry) -> None:
    assert registry.list_versions("greet") == [1, 2]
    assert registry.list_versions("nonexistent") == []


def test_latest_returns_highest_version(registry: PromptRegistry) -> None:
    assert registry.latest("greet").version == 2


def test_real_summarize_quarter_prompt_loads_and_renders() -> None:
    # Exercise the actual bundled prompt against real-shape AAPL data.
    reg = PromptRegistry()
    p = reg.get("summarize_quarter", 1)
    assert isinstance(p, Prompt)
    assert "investment advice" in p.system
    rendered = reg.render(
        p,
        {
            "name": "Apple Inc.",
            "ticker": "AAPL",
            "fiscal_year": 2025,
            "fiscal_quarter": "Q2",
            "period_end": "2025-03-29",
            "metrics": [
                {"name": "eps_diluted", "value": "1.65", "unit": "USD/shares"},
                {"name": "revenue", "value": "95359000000", "unit": "USD"},
            ],
        },
    )
    assert "Apple Inc." in rendered
    assert "AAPL" in rendered
    assert "FY2025 Q2" in rendered
    assert "2025-03-29" in rendered
    assert "eps_diluted: 1.65 USD/shares" in rendered
    assert "revenue: 95359000000 USD" in rendered

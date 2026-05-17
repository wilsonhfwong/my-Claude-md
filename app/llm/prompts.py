from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, StrictUndefined


@dataclass(frozen=True)
class Prompt:
    name: str
    version: int
    model: str
    max_tokens: int
    system: str
    user_template: str
    temperature: float | None = None
    description: str | None = None

    @property
    def id(self) -> str:
        return f"{self.name}:v{self.version}"


class PromptRegistry:
    """Versioned prompt store.

    Layout on disk:
        <root>/<name>/v<N>.toml

    Each file declares one immutable prompt. To change a prompt, add a new
    version file (`v2.toml`); never edit a published version in place, because
    the eval harness pins runs to (name, version) tuples and silent edits make
    quality regressions impossible to attribute.
    """

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or Path("prompts")
        self._cache: dict[tuple[str, int], Prompt] = {}
        self._jinja = Environment(undefined=StrictUndefined, keep_trailing_newline=True)

    def get(self, name: str, version: int) -> Prompt:
        key = (name, version)
        if key not in self._cache:
            path = self.root / name / f"v{version}.toml"
            if not path.exists():
                raise FileNotFoundError(f"No prompt at {path}")
            data = tomllib.loads(path.read_text())
            self._cache[key] = _from_toml(data, name=name, version=version)
        return self._cache[key]

    def render(self, prompt: Prompt, variables: dict[str, object]) -> str:
        template = self._jinja.from_string(prompt.user_template)
        return template.render(**variables)

    def list_versions(self, name: str) -> list[int]:
        d = self.root / name
        if not d.exists():
            return []
        versions = []
        for p in d.iterdir():
            stem = p.stem
            if stem.startswith("v") and stem[1:].isdigit():
                versions.append(int(stem[1:]))
        return sorted(versions)

    def latest(self, name: str) -> Prompt:
        versions = self.list_versions(name)
        if not versions:
            raise FileNotFoundError(f"No prompt named {name!r}")
        return self.get(name, versions[-1])


_REQUIRED_KEYS = {"model", "max_tokens", "system", "user_template"}


def _from_toml(data: dict, *, name: str, version: int) -> Prompt:
    missing = _REQUIRED_KEYS - data.keys()
    if missing:
        raise ValueError(f"Prompt {name}:v{version} missing keys: {sorted(missing)}")
    return Prompt(
        name=name,
        version=version,
        model=str(data["model"]),
        max_tokens=int(data["max_tokens"]),
        system=str(data["system"]).strip(),
        user_template=str(data["user_template"]),
        temperature=float(data["temperature"]) if "temperature" in data else None,
        description=data.get("description"),
    )

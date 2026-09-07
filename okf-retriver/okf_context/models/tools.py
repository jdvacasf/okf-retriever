from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class ParameterSpec:
    name: str
    type_name: str
    required: bool = False
    default: Any = None
    choices: tuple[str, ...] = ()
    minimum: int | None = None


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: tuple[ParameterSpec, ...]
    invoke: Callable[..., Any]
    result_type: str = "object"

    def schema(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "parameters": [parameter.__dict__ for parameter in self.parameters], "result": self.result_type}

    def __call__(self, **kwargs: Any) -> Any:
        return self.invoke(**kwargs)

from functools import wraps
from typing import Any, Callable


class AgentDebugger:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(self, agent_name: str, event: str) -> None:
        self.events.append({"agent": agent_name, "event": event})


def debug_agent(agent_name: str, debugger: AgentDebugger) -> Callable:
    def decorator(agent: Callable) -> Callable:
        @wraps(agent)
        def wrapped(state: dict[str, Any]) -> dict[str, Any]:
            debugger.record(agent_name, "started")
            result = agent(state)
            debugger.record(agent_name, "completed")
            return result

        return wrapped

    return decorator

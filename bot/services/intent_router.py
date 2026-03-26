"""Natural language router powered by LLM tool-calling."""

import json
import sys
from typing import Any, Awaitable, Callable

from .llm_api import get_llm_client, LLMError, TOOLS, SYSTEM_PROMPT
from .lms_api import get_api_client, APIError


class LLMRouter:
    """Handles user queries by delegating decisions to an LLM."""

    MAX_ITER = 5

    def __init__(self) -> None:
        self.llm = get_llm_client()
        self.api = get_api_client()

        # Mapping tool names → functions
        self.handlers: dict[str, Callable[..., Awaitable[Any]]] = {
            "get_items": self.fetch_items,
            "get_learners": self.fetch_learners,
            "get_scores": self.fetch_scores,
            "get_pass_rates": self.fetch_pass_rates,
            "get_timeline": self.fetch_timeline,
            "get_groups": self.fetch_groups,
            "get_top_learners": self.fetch_top,
            "get_completion_rate": self.fetch_completion,
            "trigger_sync": self.trigger_sync,
        }

    # ---------------- Logging ----------------

    async def _dbg(self, msg: str) -> None:
        print(f"[router] {msg}", file=sys.stderr)

    # ---------------- Tool executor ----------------

    async def execute(self, tool: str, params: dict[str, Any]) -> Any:
        if tool not in self.handlers:
            raise RuntimeError(f"Tool not found: {tool}")

        try:
            result = await self.handlers[tool](**params)
            await self._dbg(f"{tool} done ({len(str(result))} chars)")
            return result
        except APIError as e:
            await self._dbg(f"{tool} API failed: {e.message}")
            return {"error": e.message}
        except Exception as e:
            await self._dbg(f"{tool} crashed: {e}")
            return {"error": str(e)}

    # ---------------- Tool wrappers ----------------

    async def fetch_items(self) -> list[dict]:
        items = await self.api.get_items()
        return [
            {"id": x.id, "type": x.type, "title": x.title, "lab": x.lab}
            for x in items
        ]

    async def fetch_learners(self) -> list[dict]:
        return []

    async def fetch_scores(self, lab: str) -> list[dict]:
        return [{"lab": lab, "note": "not implemented"}]

    async def fetch_pass_rates(self, lab: str) -> list[dict]:
        stats = await self.api.get_pass_rates(lab)
        return [
            {"task": s.task, "pass_rate": s.pass_rate, "attempts": s.attempts}
            for s in stats
        ]

    async def fetch_timeline(self, lab: str) -> list[dict]:
        return [{"lab": lab, "note": "not implemented"}]

    async def fetch_groups(self, lab: str) -> list[dict]:
        return [{"lab": lab, "note": "not implemented"}]

    async def fetch_top(self, lab: str, limit: int = 5) -> list[dict]:
        return [{"lab": lab, "limit": limit, "note": "not implemented"}]

    async def fetch_completion(self, lab: str) -> dict:
        return {"lab": lab, "note": "not implemented"}

    async def trigger_sync(self) -> dict:
        return {"note": "not implemented"}

    # ---------------- Core logic ----------------

    async def route(self, query: str) -> str:
        await self._dbg(f"Query: {query[:50]}")

        convo = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]

        for i in range(self.MAX_ITER):
            try:
                await self._dbg(f"Step {i+1}")
                out = await self.llm.chat(convo, tools=TOOLS)

                tool_calls = out.get("tool_calls") or []

                # If no tools requested → final answer
                if not tool_calls:
                    return out.get("content") or "No answer available."

                convo.append(
                    {
                        "role": "assistant",
                        "content": out.get("content"),
                        "tool_calls": tool_calls,
                    }
                )

                for call in tool_calls:
                    fn = call.get("function", {})
                    name = fn.get("name", "")
                    raw = fn.get("arguments", "{}")

                    try:
                        args = json.loads(raw)
                    except Exception:
                        args = {}

                    await self._dbg(f"Exec {name} with {args}")

                    result = await self.execute(name, args)

                    convo.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id", ""),
                            "content": json.dumps(result)
                            if not isinstance(result, str)
                            else result,
                        }
                    )

            except LLMError as e:
                await self._dbg(f"LLM fail: {e}")
                return f"LLM error: {e}"
            except Exception as e:
                await self._dbg(f"Unexpected: {e}")
                return f"Error: {e}"

        return "Unable to process request. Try again."


# Lazy singleton
_router_instance: LLMRouter | None = None


def get_router() -> LLMRouter:
    global _router_instance
    if _router_instance is None:
        _router_instance = LLMRouter()
    return _router_instance

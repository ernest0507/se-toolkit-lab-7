"""LLM-based intent routing system for handling natural language queries."""

import json
import sys
from typing import Any, Callable, Awaitable

from .llm_api import get_llm_client, LLMError, TOOLS, SYSTEM_PROMPT
from .lms_api import get_api_client, APIError


class Router:
    """Intent router that delegates user queries to appropriate tools via LLM."""

    MAX_STEPS = 5

    def __init__(self) -> None:
        self._llm = get_llm_client()
        self._api = get_api_client()

        self._tools: dict[str, Callable[..., Awaitable[Any]]] = {
            "get_items": self._items,
            "get_learners": self._learners,
            "get_scores": self._scores,
            "get_pass_rates": self._pass_rates,
            "get_timeline": self._timeline,
            "get_groups": self._groups,
            "get_top_learners": self._top_learners,
            "get_completion_rate": self._completion,
            "trigger_sync": self._sync,
        }

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------

    async def _log(self, text: str) -> None:
        print(f"[router] {text}", file=sys.stderr)

    # ------------------------------------------------------------------
    # Tool execution
    # ------------------------------------------------------------------

    async def _run_tool(self, name: str, args: dict[str, Any]) -> Any:
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")

        try:
            result = await self._tools[name](**args)
            await self._log(f"{name} -> {len(str(result))} chars")
            return result
        except APIError as e:
            await self._log(f"{name} API error: {e.message}")
            return {"error": e.message}
        except Exception as e:
            await self._log(f"{name} exception: {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # Tool wrappers (API layer)
    # ------------------------------------------------------------------

    async def _items(self) -> list[dict]:
        data = await self._api.get_items()
        return [
            {"id": i.id, "type": i.type, "title": i.title, "lab": i.lab}
            for i in data
        ]

    async def _learners(self) -> list[dict]:
        return []

    async def _scores(self, lab: str) -> list[dict]:
        return [{"lab": lab, "note": "scores endpoint not yet implemented"}]

    async def _pass_rates(self, lab: str) -> list[dict]:
        data = await self._api.get_pass_rates(lab)
        return [
            {"task": x.task, "pass_rate": x.pass_rate, "attempts": x.attempts}
            for x in data
        ]

    async def _timeline(self, lab: str) -> list[dict]:
        return [{"lab": lab, "note": "timeline endpoint not yet implemented"}]

    async def _groups(self, lab: str) -> list[dict]:
        return [{"lab": lab, "note": "groups endpoint not yet implemented"}]

    async def _top_learners(self, lab: str, limit: int = 5) -> list[dict]:
        return [{"lab": lab, "limit": limit, "note": "not implemented"}]

    async def _completion(self, lab: str) -> dict:
        return {"lab": lab, "note": "not implemented"}

    async def _sync(self) -> dict:
        return {"note": "sync not implemented"}

    # ------------------------------------------------------------------
    # Core routing loop
    # ------------------------------------------------------------------

    async def route(self, user_input: str) -> str:
        await self._log(f"Incoming: {user_input[:50]}")

        history = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ]

        for step in range(1, self.MAX_STEPS + 1):
            try:
                await self._log(f"LLM call #{step}")
                reply = await self._llm.chat(history, tools=TOOLS)

                calls = reply.get("tool_calls", [])

                # No tools → final answer
                if not calls:
                    answer = reply.get("content") or "No information available."
                    await self._log("Final answer produced")
                    return answer

                await self._log(f"{len(calls)} tool call(s) detected")

                history.append(
                    {
                        "role": "assistant",
                        "content": reply.get("content"),
                        "tool_calls": calls,
                    }
                )

                for call in calls:
                    fn = call.get("function", {})
                    name = fn.get("name", "")
                    raw_args = fn.get("arguments", "{}")

                    try:
                        args = json.loads(raw_args) if raw_args else {}
                    except json.JSONDecodeError:
                        args = {}

                    await self._log(f"Running {name} with {args}")

                    result = await self._run_tool(name, args)

                    history.append(
                        {
                            "role": "tool",
                            "tool_call_id": call.get("id", ""),
                            "content": json.dumps(result)
                            if not isinstance(result, str)
                            else result,
                        }
                    )

                await self._log("Returning tool outputs to LLM")

            except LLMError as e:
                await self._log(f"LLM error: {e}")
                return f"LLM error: {e}"
            except Exception as e:
                await self._log(f"Unexpected failure: {e}")
                return f"Error: {e}"

        return "Request processing failed. Try rephrasing."


# Singleton pattern
_instance: Router | None = None


def get_router() -> Router:
    global _instance
    if _instance is None:
        _instance = Router()
    return _instance

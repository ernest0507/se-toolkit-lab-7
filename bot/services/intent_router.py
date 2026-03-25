"""Intent router for natural language queries using LLM tool calling."""

import json
import sys
from typing import Any

from .llm_api import get_llm_client, LLMError, TOOLS, SYSTEM_PROMPT
from .lms_api import get_api_client, APIError


class IntentRouter:
    """Routes natural language queries to backend tools via LLM."""

    def __init__(self):
        self.llm_client = get_llm_client()
        self.api_client = get_api_client()
        # Map tool names to actual functions
        self.tool_map = {
            "get_items": self._get_items,
            "get_learners": self._get_learners,
            "get_scores": self._get_scores,
            "get_pass_rates": self._get_pass_rates,
            "get_timeline": self._get_timeline,
            "get_groups": self._get_groups,
            "get_top_learners": self._get_top_learners,
            "get_completion_rate": self._get_completion_rate,
            "trigger_sync": self._trigger_sync,
        }

    async def _debug(self, message: str) -> None:
        """Print debug message to stderr."""
        print(f"[router] {message}", file=sys.stderr)

    async def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool and return the result."""
        if name not in self.tool_map:
            raise ValueError(f"Unknown tool: {name}")

        func = self.tool_map[name]
        try:
            result = await func(**arguments)
            await self._debug(f"Tool {name}({arguments}) -> {len(str(result))} chars")
            return result
        except APIError as e:
            await self._debug(f"Tool {name} error: {e.message}")
            return {"error": e.message}
        except Exception as e:
            await self._debug(f"Tool {name} exception: {e}")
            return {"error": str(e)}

    # -----------------------------------------------------------------------
    # Tool implementations - wrap LMS API calls
    # -----------------------------------------------------------------------

    async def _get_items(self) -> list[dict]:
        """Get all items (labs and tasks)."""
        items = await self.api_client.get_items()
        return [
            {"id": i.id, "type": i.type, "title": i.title, "lab": i.lab} for i in items
        ]

    async def _get_learners(self) -> list[dict]:
        """Get all learners."""
        # Note: This endpoint may not exist yet - return empty list
        return []

    async def _get_scores(self, lab: str) -> list[dict]:
        """Get score distribution for a lab."""
        # Note: This endpoint may need to be added to LMS API
        return [{"lab": lab, "note": "scores endpoint not yet implemented"}]

    async def _get_pass_rates(self, lab: str) -> list[dict]:
        """Get pass rates for a lab."""
        pass_rates = await self.api_client.get_pass_rates(lab)
        return [
            {"task": pr.task, "pass_rate": pr.pass_rate, "attempts": pr.attempts}
            for pr in pass_rates
        ]

    async def _get_timeline(self, lab: str) -> list[dict]:
        """Get timeline for a lab."""
        # Note: This endpoint may need to be added to LMS API
        return [{"lab": lab, "note": "timeline endpoint not yet implemented"}]

    async def _get_groups(self, lab: str) -> list[dict]:
        """Get group data for a lab."""
        # Note: This endpoint may need to be added to LMS API
        return [{"lab": lab, "note": "groups endpoint not yet implemented"}]

    async def _get_top_learners(self, lab: str, limit: int = 5) -> list[dict]:
        """Get top learners for a lab."""
        # Note: This endpoint may need to be added to LMS API
        return [
            {
                "lab": lab,
                "limit": limit,
                "note": "top_learners endpoint not yet implemented",
            }
        ]

    async def _get_completion_rate(self, lab: str) -> dict:
        """Get completion rate for a lab."""
        # Note: This endpoint may need to be added to LMS API
        return {"lab": lab, "note": "completion_rate endpoint not yet implemented"}

    async def _trigger_sync(self) -> dict:
        """Trigger a data sync."""
        # Note: This endpoint may need to be added to LMS API
        return {"note": "sync endpoint not yet implemented"}

    # -----------------------------------------------------------------------
    # Main routing logic
    # -----------------------------------------------------------------------

    async def route(self, message: str) -> str:
        """Route a natural language message to tools and return a response.

        Args:
            message: The user's natural language query.

        Returns:
            A text response to send back to the user.
        """
        await self._debug(f"Routing message: {message[:50]}...")

        # Build conversation history
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            try:
                # Call LLM
                await self._debug(f"Calling LLM (iteration {iteration})...")
                response = await self.llm_client.chat(messages, tools=TOOLS)

                # Check if LLM wants to call tools
                tool_calls = response.get("tool_calls", [])

                if not tool_calls:
                    # LLM provided a final answer
                    content = response.get(
                        "content", "I don't have information about that."
                    )
                    await self._debug(f"LLM returned final answer: {content[:100]}...")
                    return content

                # Execute tool calls
                await self._debug(f"LLM called {len(tool_calls)} tool(s)")

                # Add assistant's message with tool calls to history
                messages.append(
                    {
                        "role": "assistant",
                        "content": response.get("content"),
                        "tool_calls": tool_calls,
                    }
                )

                # Execute each tool call and collect results
                for tool_call in tool_calls:
                    function = tool_call.get("function", {})
                    name = function.get("name", "")
                    arguments_str = function.get("arguments", "{}")

                    try:
                        arguments = json.loads(arguments_str) if arguments_str else {}
                    except json.JSONDecodeError:
                        arguments = {}

                    await self._debug(f"Executing tool: {name}({arguments})")

                    result = await self._execute_tool(name, arguments)

                    # Add tool result to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.get("id", ""),
                            "content": json.dumps(result)
                            if not isinstance(result, str)
                            else result,
                        }
                    )

                await self._debug(
                    f"Feeding {len(tool_calls)} tool result(s) back to LLM"
                )

            except LLMError as e:
                await self._debug(f"LLM error: {e}")
                return f"LLM error: {e}"
            except Exception as e:
                await self._debug(f"Unexpected error: {e}")
                return f"Error processing request: {e}"

        # Max iterations reached
        return "I'm having trouble processing this request. Please try rephrasing your question."


# Global router instance
_router: IntentRouter | None = None


def get_router() -> IntentRouter:
    """Get or create the global intent router instance."""
    global _router
    if _router is None:
        _router = IntentRouter()
    return _router

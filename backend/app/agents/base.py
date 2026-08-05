"""Agent Base — core agent loop with tool-use and multi-turn reasoning."""
import json
import logging
from typing import AsyncGenerator
from app.config import settings
from app.core.llm import LLMClient
from app.core.memory import ConversationMemory
from app.core.tools import Tool, get_tool, get_all_tool_specs

logger = logging.getLogger(__name__)


class BaseAgent:
    """ReAct-style agent with tool-use loop."""

    def __init__(
        self,
        name: str,
        role: str,
        system_prompt: str,
        tools: list[str] | None = None,
        llm: LLMClient | None = None,
    ):
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.tool_names = tools or []
        self.llm = llm or LLMClient()
        self.memory = ConversationMemory()
        self._tools: list[Tool] = []

    def _init_tools(self):
        self._tools = []
        for name in self.tool_names:
            tool = get_tool(name)
            if tool:
                self._tools.append(tool)

    def _get_tool_specs(self) -> list[dict]:
        return [t.to_openai_spec() for t in self._tools]

    async def run(self, user_input: str, context: str = "") -> str:
        """Run the agent on a user input and return the final response."""
        self._init_tools()

        # Build system message
        system_content = self.system_prompt
        if context:
            system_content += f"\n\n## Additional Context:\n{context}"

        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.memory.get_messages())
        messages.append({"role": "user", "content": user_input})

        tool_specs = self._get_tool_specs() if self._tools else None

        for iteration in range(settings.max_iterations):
            response = await self.llm.chat(
                messages=messages,
                tools=tool_specs,
            )

            finish_reason = response.get("finish_reason", "stop")

            # Handle tool calls
            if finish_reason == "tool_calls" and response.get("tool_calls"):
                messages.append({
                    "role": "assistant",
                    "content": response.get("content", ""),
                    "tool_calls": response["tool_calls"],
                })

                for tc in response["tool_calls"]:
                    func_name = tc["function"]["name"]
                    try:
                        args = json.loads(tc["function"]["arguments"])
                    except json.JSONDecodeError:
                        args = {}

                    tool = get_tool(func_name)
                    if tool:
                        result = await tool.execute(**args)
                    else:
                        result = f"Unknown tool: {func_name}"

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": result,
                    })
                continue

            # Normal response
            content = response.get("content", "")
            self.memory.add("user", user_input)
            self.memory.add("assistant", content)
            return content

        return "Agent reached maximum iterations without a final answer."

    async def run_stream(self, user_input: str, context: str = "") -> AsyncGenerator[str, None]:
        """Run agent with streaming output (no tool loop for simplicity)."""
        system_content = self.system_prompt
        if context:
            system_content += f"\n\n## Additional Context:\n{context}"

        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.memory.get_messages())
        messages.append({"role": "user", "content": user_input})

        async for chunk in self.llm.chat_stream(messages):
            yield chunk

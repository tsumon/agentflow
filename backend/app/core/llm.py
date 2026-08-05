"""LLM Client — unified interface for OpenAI-compatible APIs."""
import json
from typing import AsyncGenerator
from openai import AsyncOpenAI
from app.config import settings


class LLMClient:
    """Async LLM client with streaming support."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )
        self.model = settings.llm_model

    async def chat(
        self,
        messages: list[dict],
        temperature: float | None = None,
        max_tokens: int | None = None,
        tools: list[dict] | None = None,
    ) -> dict:
        """Non-streaming chat completion."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or settings.llm_temperature,
            max_tokens=max_tokens or settings.llm_max_tokens,
            tools=tools,
        )
        choice = response.choices[0]
        msg = choice.message

        result = {
            "role": "assistant",
            "content": msg.content or "",
        }

        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        if choice.finish_reason:
            result["finish_reason"] = choice.finish_reason

        return result

    async def chat_stream(
        self,
        messages: list[dict],
        temperature: float | None = None,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat completion."""
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature or settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton
llm_client = LLMClient()

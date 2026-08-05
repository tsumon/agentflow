"""Agent Tools — built-in tool registry for agents."""
import json
import math
import re
from typing import Any, Callable


class Tool:
    """A callable tool with JSON Schema definition."""

    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict,
        func: Callable,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func

    def to_openai_spec(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    async def execute(self, **kwargs) -> str:
        result = self.func(**kwargs)
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False, indent=2)


# --- Built-in Tools ---

def tool_calculator(expression: str) -> str:
    """Evaluate a mathematical expression."""
    try:
        allowed = set("0123456789+-*/().,%^ absintfloatroundsincostanlogsqrtpie")
        cleaned = "".join(c for c in expression if c in allowed or c.isspace())
        result = eval(cleaned, {"__builtins__": {}}, {
            "abs": abs, "int": int, "float": float,
            "round": round, "sin": math.sin, "cos": math.cos,
            "tan": math.tan, "log": math.log, "sqrt": math.sqrt,
            "pi": math.pi, "e": math.e, "pow": pow,
        })
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


def tool_search(query: str) -> str:
    """Simulated search tool (placeholder for real search integration)."""
    return json.dumps({
        "query": query,
        "results": [
            {"title": f"Result 1 for '{query}'", "snippet": f"Relevant information about {query}..."},
            {"title": f"Result 2 for '{query}'", "snippet": f"More details on {query}..."},
        ],
        "note": "This is a simulated search. Integrate with real search API for production."
    }, ensure_ascii=False)


def tool_read_file(path: str) -> str:
    """Read a file from the filesystem."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:5000] + ("\n...(truncated)" if len(content) > 5000 else "")
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {e}"


def tool_write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Error writing file: {e}"


def tool_web_fetch(url: str) -> str:
    """Fetch content from a URL."""
    import urllib.request
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = resp.read().decode("utf-8", errors="replace")
        return data[:3000] + ("\n...(truncated)" if len(data) > 3000 else "")
    except Exception as e:
        return f"Error fetching {url}: {e}"


def tool_json_parse(text: str) -> str:
    """Extract and parse JSON from text."""
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.dumps(json.loads(match.group()), ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pass
        match = re.search(r'\[[\s\S]*\]', text)
        if match:
            try:
                return json.dumps(json.loads(match.group()), ensure_ascii=False, indent=2)
            except json.JSONDecodeError:
                pass
        return f"Could not parse JSON from: {text[:200]}"


# Tool Registry
TOOL_REGISTRY: dict[str, Tool] = {
    "calculator": Tool(
        name="calculator",
        description="Evaluate a mathematical expression. Supports +-*/^, sin/cos/tan/log/sqrt, pi/e.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate, e.g. '2+3*4' or 'sqrt(16)'."
                }
            },
            "required": ["expression"],
        },
        func=tool_calculator,
    ),
    "search": Tool(
        name="search",
        description="Search for information on a given topic.",
        parameters={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query."
                }
            },
            "required": ["query"],
        },
        func=tool_search,
    ),
    "read_file": Tool(
        name="read_file",
        description="Read the contents of a file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the file."
                }
            },
            "required": ["path"],
        },
        func=tool_read_file,
    ),
    "write_file": Tool(
        name="write_file",
        description="Write content to a file.",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute path to the file."
                },
                "content": {
                    "type": "string",
                    "description": "Content to write."
                }
            },
            "required": ["path", "content"],
        },
        func=tool_write_file,
    ),
    "web_fetch": Tool(
        name="web_fetch",
        description="Fetch content from a URL.",
        parameters={
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch."
                }
            },
            "required": ["url"],
        },
        func=tool_web_fetch,
    ),
    "json_parse": Tool(
        name="json_parse",
        description="Extract and pretty-print JSON from text.",
        parameters={
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text containing JSON."
                }
            },
            "required": ["text"],
        },
        func=tool_json_parse,
    ),
}


def get_tool(name: str) -> Tool | None:
    return TOOL_REGISTRY.get(name)


def get_all_tool_specs() -> list[dict]:
    return [t.to_openai_spec() for t in TOOL_REGISTRY.values()]

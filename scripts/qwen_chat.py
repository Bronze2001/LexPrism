#!/usr/bin/env python3
"""Direct Qwen + LexPrism + PKULaw MCP test client.

Qwen selects function calls; this program performs the selected read-only MCP
calls and returns their actual result to Qwen. It never enables a code
interpreter. Public web search is opt-in because a LexPrism task can be limited
to user-provided materials.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import urllib.error
import urllib.request
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SKILL = PROJECT_ROOT / "skills" / "lexprism" / "SKILL.md"
DEFAULT_BASE_URL = "https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1"
DEFAULT_MODEL = "qwen3.8-max"
PKULAW_SERVERS = {
    "law_search": "https://apim-gateway.pkulaw.com/mcp-law-search-service",
    "law_keyword": "https://apim-gateway.pkulaw.com/mcp-law",
    "fatiao_keyword": "https://apim-gateway.pkulaw.com/mcp-fatiao",
    "case_search": "https://apim-gateway.pkulaw.com/mcp-case-search-service",
    "citation_validator": "https://apim-gateway.pkulaw.com/pku_citation_validator",
}


def load_dotenv(path: Path) -> None:
    """Load simple KEY=VALUE pairs without printing secret values."""
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() and key.strip() not in os.environ:
            os.environ[key.strip()] = value.strip()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def text_from_mcp_result(result: Any) -> str:
    """Preserve MCP output without interpreting it as evidence."""
    parts: list[str] = []
    for item in result.content:
        if hasattr(item, "text"):
            parts.append(item.text)
        elif hasattr(item, "model_dump"):
            parts.append(json.dumps(item.model_dump(mode="json"), ensure_ascii=False))
        else:
            parts.append(str(item))
    return ("MCP tool reported an error.\n" if result.isError else "") + "\n".join(parts)


class PKULawMCP:
    """Connect the project's first-run PKULaw services and expose live tools."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._stack = AsyncExitStack()
        self._tool_routes: dict[str, tuple[ClientSession, str, Any]] = {}

    async def __aenter__(self) -> "PKULawMCP":
        for alias, url in PKULAW_SERVERS.items():
            read, write, _session_id = await self._stack.enter_async_context(
                streamablehttp_client(url, headers={"Authorization": f"Bearer {self._token}"})
            )
            session = await self._stack.enter_async_context(ClientSession(read, write))
            await session.initialize()
            for tool in (await session.list_tools()).tools:
                name = f"pkulaw__{safe_name(alias)}__{safe_name(tool.name)}"
                if name in self._tool_routes:
                    raise RuntimeError(f"Duplicate exposed MCP tool name: {name}")
                self._tool_routes[name] = (session, tool.name, tool)
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self._stack.aclose()

    def qwen_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.description or f"PKULaw MCP tool: {native_name}",
                    "parameters": tool.inputSchema,
                },
            }
            for name, (_session, native_name, tool) in self._tool_routes.items()
        ]

    def tool_names(self) -> list[str]:
        return sorted(self._tool_routes)

    async def call(self, name: str, arguments: dict[str, Any]) -> str:
        try:
            session, native_name, _tool = self._tool_routes[name]
        except KeyError as error:
            raise RuntimeError(f"Qwen requested an unavailable tool: {name}") from error
        return text_from_mcp_result(await session.call_tool(native_name, arguments))


SKILL_REFERENCE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_skill_reference",
        "description": "Read a packaged LexPrism workflow reference by filename. Load references required by the task routing before performing that workflow. This reads skill instructions, not user documents or legal sources.",
        "parameters": {
            "type": "object",
            "properties": {"filename": {"type": "string", "description": "Exact .md filename listed in the skill reference catalog."}},
            "required": ["filename"],
            "additionalProperties": False,
        },
    },
}


def skill_references(skill_path: Path) -> dict[str, Path]:
    directory = (skill_path.parent / "references").resolve()
    return {
        path.name: path
        for path in sorted(directory.glob("*.md"))
        if path.is_file() and path.resolve().parent == directory
    }


def read_skill_reference(skill_path: Path, arguments: dict[str, Any]) -> str:
    if not isinstance(arguments, dict) or set(arguments) != {"filename"}:
        raise ValueError("Expected only a filename argument.")
    filename = arguments["filename"]
    if not isinstance(filename, str) or filename not in skill_references(skill_path):
        raise ValueError("Unavailable skill reference; use an exact catalog filename.")
    return skill_references(skill_path)[filename].read_text(encoding="utf-8")


def build_system_message(skill_path: Path, include_research_references: bool) -> str:
    skill_text = skill_path.read_text(encoding="utf-8")
    message = (
        "Apply the following LexPrism skill as the governing workflow. Use a PKULaw "
        "function only when the user permits legal research. Treat tool output as "
        "provider material: distinguish snippets, database reports, and retrieved "
        "original text. Do not claim a tool ran unless its result appears here.\n\n"
        f"--- BEGIN SKILL: {skill_path.name} ---\n{skill_text}\n--- END SKILL ---"
    )
    message += (
        "\n\nUse read_skill_reference to load task-specific workflows and their linked references "
        "before applying them. Packaged reference catalog: "
        + ", ".join(skill_references(skill_path))
    )
    if not include_research_references:
        return message
    for filename in ("research.md", "data-and-tools.md"):
        reference_path = skill_path.parent / "references" / filename
        message += (
            f"\n\n--- BEGIN SKILL REFERENCE: {filename} ---\n"
            f"{reference_path.read_text(encoding='utf-8')}\n"
            "--- END SKILL REFERENCE ---"
        )
    return message


def post_chat(base_url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Qwen API returned HTTP {error.code}: {detail}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"Could not reach the Qwen API: {error.reason}") from error


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ask Qwen 3.8-Max with LexPrism and PKULaw MCP tools.")
    parser.add_argument("prompt", nargs="?", help="Question or task to send to Qwen.")
    parser.add_argument("--skill", type=Path, default=DEFAULT_SKILL, help="Path to SKILL.md.")
    parser.add_argument("--model", default=os.getenv("QWEN_MODEL", DEFAULT_MODEL))
    parser.add_argument("--base-url", default=os.getenv("DASHSCOPE_BASE_URL", DEFAULT_BASE_URL))
    parser.add_argument("--web-search", choices=("off", "on"), default="off", help="Opt in to Qwen public web search.")
    parser.add_argument("--list-tools", action="store_true", help="List PKULaw tools without calling Qwen.")
    parser.add_argument("--dry-run", action="store_true", help="Validate local settings without network calls.")
    parser.add_argument("--max-tool-rounds", type=int, default=6)
    return parser.parse_args()


async def run(args: argparse.Namespace) -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    skill_path = args.skill.resolve()
    if not skill_path.is_file():
        print(f"Skill file not found: {skill_path}", file=sys.stderr)
        return 2
    if args.dry_run:
        build_system_message(skill_path, include_research_references=True)
        print(json.dumps({"model": args.model, "skill": str(skill_path), "code_interpreter": "absent", "web_search": args.web_search}, ensure_ascii=False))
        return 0
    if args.max_tool_rounds < 1:
        print("--max-tool-rounds must be at least 1.", file=sys.stderr)
        return 2
    token = os.getenv("PKULAW_MCP_TOKEN")
    if not token:
        print("Set PKULAW_MCP_TOKEN in the Windows user environment or .env.", file=sys.stderr)
        return 2
    async with PKULawMCP(token) as mcp:
        if args.list_tools:
            print("\n".join(mcp.tool_names()))
            return 0
        if not args.prompt:
            print("Provide a prompt unless --list-tools or --dry-run is used.", file=sys.stderr)
            return 2
        if "{WorkspaceId}" in args.base_url:
            print("Set DASHSCOPE_BASE_URL with your actual Bailian WorkspaceId.", file=sys.stderr)
            return 2
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            print("Set DASHSCOPE_API_KEY in .env or the environment before calling Qwen.", file=sys.stderr)
            return 2

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": build_system_message(skill_path, include_research_references=True)},
            {"role": "user", "content": args.prompt},
        ]
        for _round in range(args.max_tool_rounds):
            payload: dict[str, Any] = {
                "model": args.model,
                "messages": messages,
                "tools": [SKILL_REFERENCE_TOOL, *mcp.qwen_tools()],
                "tool_choice": "auto",
                "parallel_tool_calls": False,
                "enable_thinking": False,
            }
            if args.web_search == "on":
                payload["enable_search"] = True
                payload["search_options"] = {"search_strategy": "max", "enable_source": True, "enable_citation": True}
            response = post_chat(args.base_url, api_key, payload)
            try:
                assistant = response["choices"][0]["message"]
            except (KeyError, IndexError, TypeError) as error:
                raise RuntimeError(f"Unexpected Qwen API response: {json.dumps(response, ensure_ascii=False)}") from error
            tool_calls = assistant.get("tool_calls") or []
            messages.append({"role": "assistant", "content": assistant.get("content"), "tool_calls": tool_calls})
            if not tool_calls:
                print(assistant.get("content") or "")
                return 0
            for tool_call in tool_calls:
                function = tool_call["function"]
                try:
                    arguments = json.loads(function.get("arguments") or "{}")
                    if function["name"] == "read_skill_reference":
                        tool_result = read_skill_reference(skill_path, arguments)
                    else:
                        tool_result = await mcp.call(function["name"], arguments)
                except (ValueError, RuntimeError, OSError) as error:
                    tool_result = f"Tool call failed: {error}"
                messages.append({"role": "tool", "tool_call_id": tool_call["id"], "content": tool_result})
        raise RuntimeError(f"Stopped after {args.max_tool_rounds} tool rounds without a final answer.")


def main() -> int:
    try:
        return asyncio.run(run(parse_args()))
    except (RuntimeError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

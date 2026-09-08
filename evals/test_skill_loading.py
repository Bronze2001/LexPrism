"""Offline checks for packaged workflow access; no model or legal validation."""

import asyncio
import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("qwen_chat", ROOT / "scripts/qwen_chat.py")
chat = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(chat)


class SkillLoadingTests(unittest.TestCase):
    def test_packaged_workflows_are_readable(self):
        for name, path in chat.skill_references(chat.DEFAULT_SKILL).items():
            self.assertEqual(
                chat.read_skill_reference(chat.DEFAULT_SKILL, {"filename": name}),
                path.read_text(encoding="utf-8"),
            )

    def test_arbitrary_files_and_malformed_arguments_are_rejected(self):
        for value in ["../SKILL.md", "../../.env", str(ROOT / ".env"), "missing.md", None, []]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                chat.read_skill_reference(chat.DEFAULT_SKILL, {"filename": value})
        for args in [[], {}, {"filename": "research.md", "other": True}]:
            with self.assertRaises(ValueError):
                chat.read_skill_reference(chat.DEFAULT_SKILL, args)

    def test_model_reference_call_returns_to_conversation_without_mcp_dispatch(self):
        class FakeMCP:
            def __init__(self, token):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                pass

            def qwen_tools(self):
                return []

            async def call(self, *args):
                raise AssertionError("Local skill reference must not reach MCP")

        turns = []

        def fake_post(base_url, api_key, payload):
            turns.append(True)
            if len(turns) == 1:
                self.assertIn(chat.SKILL_REFERENCE_TOOL, payload["tools"])
                return {"choices": [{"message": {"content": None, "tool_calls": [{
                    "id": "ref-1", "type": "function", "function": {
                        "name": "read_skill_reference",
                        "arguments": '{"filename":"contract-review.md"}',
                    },
                }]}}]}
            self.assertEqual(payload["messages"][-1]["role"], "tool")
            self.assertEqual(payload["messages"][-1]["tool_call_id"], "ref-1")
            self.assertEqual(payload["messages"][-1]["content"],
                             (chat.DEFAULT_SKILL.parent / "references/contract-review.md").read_text(encoding="utf-8"))
            return {"choices": [{"message": {"content": "offline completion"}}]}

        args = SimpleNamespace(skill=chat.DEFAULT_SKILL, dry_run=False, max_tool_rounds=2,
                               list_tools=False, prompt="审核合同", base_url="https://invalid.example",
                               model="offline-test", web_search="off")
        with patch.object(chat, "PKULawMCP", FakeMCP), patch.object(chat, "post_chat", fake_post), \
                patch.object(chat, "load_dotenv"), patch.dict(chat.os.environ, {
                    "PKULAW_MCP_TOKEN": "fake", "DASHSCOPE_API_KEY": "fake",
                }), patch("builtins.print"):
            self.assertEqual(asyncio.run(chat.run(args)), 0)
        self.assertEqual(len(turns), 2)


if __name__ == "__main__":
    unittest.main()

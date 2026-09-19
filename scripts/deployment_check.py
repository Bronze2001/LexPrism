"""Offline deployment checks. Never read credentials or patch the host configuration."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys
from urllib.parse import urlsplit


TOKEN = "Bearer <YOUR_PKULAW_BEARER_TOKEN>"


def validate_mcp(data):
    services = data.get("mcpServers")
    if not isinstance(services, dict) or not services:
        raise ValueError("Missing MCP service definitions.")
    for name, service in services.items():
        if service.get("type") == "stdio":
            if set(service) != {"type", "command", "args", "env"}:
                raise ValueError("Unexpected local MCP configuration fields.")
            if service.get("command") != "npx" or service.get("args") != ["-y", "@cyanheads/eur-lex-mcp-server@0.12.1"]:
                raise ValueError("Unexpected local MCP command or package version.")
            if service.get("env") != {"MCP_TRANSPORT_TYPE": "stdio", "MCP_LOG_LEVEL": "info"}:
                raise ValueError("Unexpected local MCP environment; secrets do not belong in the template.")
        else:
            if not set(service) <= {"type", "url", "headers"}:
                raise ValueError("Unexpected remote MCP configuration fields.")
            u = urlsplit(service.get("url", ""))
            if service.get("type") != "streamable-http" or u.scheme != "https" or not u.hostname or u.username or u.password:
                raise ValueError("Invalid remote MCP URL or transport.")
            if name.startswith("pkulaw-"):
                if service.get("headers") != {"Authorization": TOKEN}:
                    raise ValueError("PKULaw template must contain only the credential placeholder.")
            elif service.get("headers"):
                raise ValueError("Unexpected credentials in a public MCP template.")
    return len(services)


def check(root):
    required = ["PROJECT.md", "AGENTS.md", "scripts/document_workflow.py", "config/mcp-servers.template.json",
                "skills/lexprism/SKILL.md", "skills/lexprism-review/SKILL.md", "skills/drawio-diagram/SKILL.md",
                "templates/legal-project/PROJECT.md", "templates/legal-project/AGENTS.md"]
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise ValueError("Missing deployment files: " + ", ".join(missing))
    if sys.version_info < (3, 10):
        raise ValueError("Python 3.10 or newer is required for the local workflow.")
    data = json.loads((root / "config/mcp-servers.template.json").read_text(encoding="utf-8-sig"))
    count = validate_mcp(data)
    manifest = root / "deployment-manifest.json"
    if manifest.exists():
        for name, sha in json.loads(manifest.read_text(encoding="utf-8"))["files"].items():
            target = root / name
            if Path(name).is_absolute() or ".." in Path(name).parts or not target.resolve().is_relative_to(root.resolve()):
                raise ValueError("Unsafe package manifest path.")
            if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != sha:
                raise ValueError("Deployment file changed or missing: " + name)
    return {"offline_package_check": "PASS", "mcp_template_services": count,
            "python": ".".join(map(str, sys.version_info[:3])),
            "node_available": bool(shutil.which("node")), "npx_available": bool(shutil.which("npx")),
            "eurlex_requires": "Optional npm package 0.12.1; Node >=24 according to provider metadata; startup not tested here.",
            "live_checks": "NOT_PERFORMED: Qwen import, shared-directory access, Word rendering, MCP authentication and sample retrieval",
            "credentials": "Fill privately in Qwen; this checker neither reads credentials nor installs connectors."}


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.root.resolve()), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError) as error:
        print(json.dumps({"offline_package_check": "FAIL", "error": str(error)}, ensure_ascii=False))
        raise SystemExit(1)

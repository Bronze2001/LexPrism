"""Sync text standards; package all three skills and the complete project kit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import posixpath
from pathlib import Path
from urllib.parse import unquote
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

try:
    from .deployment_check import validate_mcp
except ImportError:
    from deployment_check import validate_mcp


ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "skills" / "lexprism"
REVIEWER = ROOT / "skills" / "lexprism-review"
DRAWING = ROOT / "skills" / "drawio-diagram"
PROJECT_SKILLS = (GENERATOR, REVIEWER, DRAWING)
# The legacy diagrams reference stays with the existing generator tree unchanged;
# the text reviewer does not invoke its independent drawing workflow.
EXCLUDED_SHARED = {"diagrams.md"}
PACKAGE_REVISION = "docs1"
SKILL_LABELS = {"lexprism": "法律研究与文书", "lexprism-review": "法律文稿复核",
                "drawio-diagram": "股权与交易图"}


def skill_archive_name(folder: Path, qwen: bool = True) -> str:
    host = "千问导入" if qwen else "通用技能"
    return f"LexPrism-{SKILL_LABELS[folder.name]}-{host}-{skill_version(folder)}.zip"


def package_version() -> str:
    return f"{skill_version(GENERATOR)}-{PACKAGE_REVISION}"


def project_archive_name(qwen: bool = True) -> str:
    host = "千问版" if qwen else "通用版"
    return f"LexPrism-完整工作区-{host}-{package_version()}.zip"


def skill_files(folder: Path) -> list[Path]:
    """Include maintained instructions and UI metadata, never local runtime state."""
    return [folder / "SKILL.md", *sorted((folder / "references").glob("*.md")),
            *sorted((folder / "agents").glob("*.yaml"))]


def skill_version(folder: Path) -> str:
    content = (folder / "SKILL.md").read_text(encoding="utf-8")
    match = re.search(r"^  version: ([a-zA-Z0-9.-]+)$", content, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing version: {folder}")
    return match.group(1)


def qwen_payload(folder: Path) -> dict[str, bytes]:
    """Adapt host-specific frontmatter without duplicating legal instructions."""
    settings = json.loads((ROOT / "packaging" / "qwen-ui.json").read_text(encoding="utf-8"))[folder.name]
    required = ("name_en", "name_zh", "description_en", "argument-hint-en", "argument-hint-zh")
    if any(not isinstance(settings.get(key), str) or not settings[key].strip() for key in required):
        raise ValueError(f"Incomplete Qwen display metadata: {folder.name}")
    examples = settings.get("examples", [])
    seen = set()
    for example in examples:
        if not example.get("id") or example["id"] in seen:
            raise ValueError(f"Missing or duplicate Qwen example ID: {folder.name}")
        seen.add(example["id"])
        for field in ("title", "description", "prompt"):
            if any(not isinstance(example.get(field, {}).get(lang), str)
                   or not example[field][lang].strip() for lang in ("zh", "en")):
                raise ValueError(f"Incomplete bilingual example: {folder.name}/{example['id']}")
    if not 2 <= len(examples) <= 5:
        raise ValueError(f"Expected 2-5 Qwen examples: {folder.name}")
    content = (folder / "SKILL.md").read_text(encoding="utf-8")
    _, header, body = content.split("---", 2)
    description_zh = re.search(r"^description: (.+)$", header, re.MULTILINE).group(1)
    fields = {"name": folder.name, **{key: settings[key] for key in required},
              "description": settings["description_en"], "description_zh": description_zh,
              "argument-hint": settings["argument-hint-en"], "user-invocable": True}
    # JSON scalar encoding is also valid YAML and safely quotes punctuation.
    lines = [f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in fields.items()]
    lines.extend(["metadata:", f"  version: {skill_version(folder)}"])
    skill = "---\n" + "\n".join(lines) + "\n---" + body
    return {"SKILL.md": skill.encode("utf-8"),
            ".skill-metadata.yaml": (json.dumps({"examples": examples}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")}


def write_archive(output: Path, contents: dict[str, bytes]) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        with ZipFile(output) as prior:
            if prior.testzip() is None and set(prior.namelist()) == set(contents) and all(prior.read(k) == v for k,v in contents.items()):
                print(f"Unchanged archive retained: {output.name}")
                return
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for name, data in sorted(contents.items()):
            entry = ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    with ZipFile(output) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(contents):
            raise ValueError(f"Archive integrity check failed: {output}")
        for name, data in contents.items():
            if archive.read(name) != data:
                raise ValueError(f"Archive mismatch: {name}")
    print(f"Built {output.name}: {len(contents)} files, {output.stat().st_size} bytes")


def shared_references() -> list[Path]:
    return sorted(p for p in (GENERATOR / "references").glob("*.md")
                  if p.name not in EXCLUDED_SHARED)


def check_local_links(folder: Path) -> None:
    """Ensure each skill's Markdown references resolve inside its own package."""
    for document in folder.rglob("*.md"):
        content = document.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]\n]*\]\(([^)]+)\)", content):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                continue
            target = (document.parent / link.split("#", 1)[0]).resolve()
            if not target.is_relative_to(folder.resolve()) or not target.is_file():
                raise ValueError(f"Unresolved package reference: {document}: {link}")


def build(check_only: bool) -> None:
    validate_mcp(json.loads((ROOT / "config/mcp-servers.template.json").read_text(encoding="utf-8-sig")))
    for source in shared_references():
        target = REVIEWER / "references" / source.name
        if check_only:
            if not target.exists() or target.read_bytes() != source.read_bytes():
                raise ValueError(f"Shared reference out of sync: {target}")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())

    for folder in PROJECT_SKILLS:
        check_local_links(folder)
        adapted = qwen_payload(folder)
        if check_only:
            continue
        contents = {p.relative_to(folder.parent).as_posix(): p.read_bytes() for p in skill_files(folder)}
        write_archive(ROOT / "dist" / skill_archive_name(folder, False), contents)
        contents.update({f"{folder.name}/{name}": data for name, data in adapted.items()})
        write_archive(ROOT / "dist" / skill_archive_name(folder), contents)
    print("Shared text references and package links are valid.")
    if not check_only:
        build_project_kit()
        write_dist_index()


def build_project_kit() -> None:
    """Bundle the runtime separately from independently importable skill ZIPs."""
    version = package_version()
    files = {
        "README.md": ROOT / "templates" / "project-workspace" / "README.md",
        "docs/一次性部署说明.md": ROOT / "docs" / "一次性部署说明.md",
        "docs/律师使用说明.md": ROOT / "docs" / "律师使用说明.md",
        "docs/项目协作操作说明.md": ROOT / "docs" / "项目协作操作说明.md",
        "AGENTS.md": ROOT / "templates" / "project-workspace" / "AGENTS.md",
        "PROJECT.md": ROOT / "templates" / "project-workspace" / "PROJECT.md",
        "scripts/document_workflow.py": ROOT / "scripts" / "document_workflow.py",
        "scripts/deployment_check.py": ROOT / "scripts" / "deployment_check.py",
        "config/mcp-servers.template.json": ROOT / "config/mcp-servers.template.json",
        "config/mcp-catalog.json": ROOT / "config/mcp-catalog.json",
        "scripts/generate_diagram.py": ROOT / "scripts" / "generate_diagram.py",
        "scripts/verify_diagram.py": ROOT / "scripts" / "verify_diagram.py",
        "evals/templates/diagram_plan.template.json": ROOT / "evals" / "templates" / "diagram_plan.template.json",
        "THIRD_PARTY_NOTICES.md": ROOT / "THIRD_PARTY_NOTICES.md",
    }
    for folder in PROJECT_SKILLS:
        for path in skill_files(folder):
            files[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / "templates" / "legal-project").glob("*.md"):
        files[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / "tools" / "drawio").rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".html", ".drawio"}:
            files[path.relative_to(ROOT).as_posix()] = path
    for path in (ROOT / "docs/workflow-design-2026-09-17").glob("*"):
        if path.suffix.lower() in {".png", ".svg", ".drawio"}:
            files[path.relative_to(ROOT).as_posix()] = path
    for folder in PROJECT_SKILLS:
        archive_name = skill_archive_name(folder)
        files[f"skill-imports/{archive_name}"] = ROOT / "dist" / archive_name
    expected_skills = {f"skills/{folder.name}/SKILL.md" for folder in PROJECT_SKILLS}
    included_skills = {name for name in files if name.startswith("skills/") and name.endswith("/SKILL.md")}
    if included_skills != expected_skills or len(included_skills) != 3:
        raise ValueError("Project kit must contain generator, reviewer and drawing skills")
    contents = {f"lexprism-project/{name}": path.read_bytes() for name, path in files.items()}
    import_guide = ["# 千问技能导入清单", "", "分别导入下列 ZIP；完整工作区 ZIP 应解压使用。", "",
                    "| 文件 | 对应窗口 / 用途 |", "| --- | --- |"]
    for folder in PROJECT_SKILLS:
        name = skill_archive_name(folder)
        import_guide.append(f"| [{name}]({name}) | {SKILL_LABELS[folder.name]}（{folder.name}） |")
    import_guide.extend(["", "生成和复核在两个真实对话中进行；绘图按需使用。安装与验收见 [部署说明](../docs/一次性部署说明.md)。", ""])
    contents["lexprism-project/skill-imports/README.md"] = "\n".join(import_guide).encode("utf-8")
    versions = ["# 包与组件版本", "", f"完整工作区：{version}。docs1 为文档与包装修订，不代表法律规则或运行程序升级。", "",
                "| 组件 | 版本 |", "| --- | --- |"]
    versions.extend(f"| {SKILL_LABELS[folder.name]} | {skill_version(folder)} |" for folder in PROJECT_SKILLS)
    versions.extend(["| 事项与发布程序 | 0.8.0-two-window |", "",
                     "独立技能 ZIP 与 skills 目录分别用于安装和工作区直接读取；生成与审阅内的共用参考是独立导入所需副本，由构建程序同步。", ""])
    contents["lexprism-project/版本信息.md"] = "\n".join(versions).encode("utf-8")
    services = json.loads((ROOT / "config/mcp-servers.template.json").read_text(encoding="utf-8-sig"))["mcpServers"]
    groups = {"mcp-pkulaw.template.json": {k:v for k,v in services.items() if k.startswith("pkulaw-")},
              "mcp-overseas.template.json": {k:v for k,v in services.items() if not k.startswith("pkulaw-") and v["type"] != "stdio"},
              "mcp-eurlex.optional.json": {k:v for k,v in services.items() if v["type"] == "stdio"}}
    for name, group in groups.items():
        validate_mcp({"mcpServers": group})
        contents[f"lexprism-project/config/{name}"] = (json.dumps({"mcpServers": group}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    add_deployment_manifest(contents, version)
    check_archive_links(contents)
    write_archive(ROOT / "dist" / project_archive_name(False), contents)
    for folder in PROJECT_SKILLS:
        contents.update({f"lexprism-project/skills/{folder.name}/{name}": data
                         for name, data in qwen_payload(folder).items()})
    add_deployment_manifest(contents, version)
    write_archive(ROOT / "dist" / project_archive_name(), contents)


def check_archive_links(contents: dict[str, bytes]) -> None:
    """Resolve links after relocation into the package, not against the source tree."""
    for name, data in contents.items():
        if not name.endswith(".md"):
            continue
        for link in re.findall(r"\[[^\]\n]*\]\(([^)]+)\)", data.decode("utf-8")):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", link) or link.startswith("#"):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(link.split("#", 1)[0])))
            if target not in contents:
                raise ValueError(f"Unresolved deployment reference: {name}: {link}")


def write_dist_index() -> None:
    """Label every retained ZIP; keep historical archives and their names intact."""
    current = {project_archive_name(): "首次安装：完整工作区，解压使用（含三个千问技能导入包）",
               project_archive_name(False): "通用工作区：技能采用通用字段；内附的独立导入 ZIP 仍是千问版"}
    for folder in PROJECT_SKILLS:
        current[skill_archive_name(folder)] = f"千问单独导入：{SKILL_LABELS[folder.name]}"
        current[skill_archive_name(folder, False)] = f"通用技能：{SKILL_LABELS[folder.name]}，无千问专用卡片字段"
    lines = ["# ZIP 选择与历史包索引", "", f"当前文档与包装修订：{package_version()}。本表由打包程序生成。", "",
             "首次安装选 **完整工作区-千问版**，解压后按包内 README 操作。只更新某项技能选对应的 **千问导入** ZIP。", "",
             "## 当前包", "", "| ZIP | 用途 |", "| --- | --- |"]
    lines.extend(f"| [{name}]({name}) | {purpose} |" for name, purpose in current.items())
    lines.extend(["", "通用版与千问版的法律规则相同，区别在技能卡片字段。docs1 只标识完整工作区的文档与包装修订；单项技能版本以当前包文件名及包内版本信息为准。", "",
                  "## 历史包（保留，不作为首次安装入口）", "",
                  "以下逐包检查 ZIP 内容并按用途标注；版本沿用原文件名，不能仅凭时间判断最新规则。", "",
                  "| 原 ZIP | 内容 / 用法 | 备注 |", "| --- | --- | --- |"])
    seen_hashes = {}
    for path in sorted((ROOT / "dist").glob("*.zip")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if path.name in current:
            seen_hashes[digest] = path.name
    for path in sorted((ROOT / "dist").glob("*.zip")):
        if path.name in current:
            continue
        with ZipFile(path) as archive:
            names = archive.namelist()
            if archive.testzip() is not None:
                raise ValueError(f"Invalid historical ZIP: {path.name}")
        entries = [n.split("/")[-2] for n in names if n.endswith("/SKILL.md")]
        if len(entries) > 1:
            purpose = "多技能工作区，解压使用"
        else:
            purpose = "单技能：" + "/".join(SKILL_LABELS.get(n, n) for n in entries)
        purpose += "；千问版" if path.stem.endswith("-qwen") else "；通用 / 早期格式"
        if any("/skill-imports/" in n for n in names):
            purpose += "；内含独立导入包"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        note = f"与 {seen_hashes[digest]} 字节完全相同" if digest in seen_hashes else "历史留存"
        seen_hashes.setdefault(digest, path.name)
        lines.append(f"| [{path.name}]({path.name}) | {purpose} | {note} |")
    lines.extend(["", "旧 project 千问包与 deployment 千问包如标为字节相同，只需选一份；新版统一为“完整工作区”，不再生成两个别名。", "",
                  "历史 ZIP 未删除、移动或改写。包的结构检查不代表千问实际导入、Word 页面或法律质量已经验证。", ""])
    (ROOT / "dist" / "README.md").write_text("\n".join(lines), encoding="utf-8")


def add_deployment_manifest(contents, version):
    key = "lexprism-project/deployment-manifest.json"
    manifest = {"version": version, "files": {name.removeprefix("lexprism-project/"): hashlib.sha256(data).hexdigest()
                for name, data in sorted(contents.items()) if name != key}}
    contents[key] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing files")
    build(parser.parse_args().check)

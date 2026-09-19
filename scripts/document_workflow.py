"""Local document submission/review records. No Git, network, or model calls."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import sys
import time
import unicodedata
import uuid
import xml.etree.ElementTree as ET
from zipfile import ZipFile, BadZipFile


TEMPLATES = Path(__file__).resolve().parents[1] / "templates" / "legal-project"
CHECKS = ("evidence", "coverage", "prose", "views")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv"}
RUNTIME_VERSION = "0.8.0-two-window"


class WorkflowError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def atomic_write(path, data):
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def publish_directory(staging, destination):
    """Publish once; tolerate brief Windows file-handle contention, not bad ACLs."""
    parent = staging.parent.resolve()
    if staging.resolve().parent != parent or destination.resolve().parent != parent:
        raise WorkflowError("Publication paths must remain in the same project directory.")
    for attempt, delay in enumerate((0.05, 0.15, 0.35, 0)):
        if destination.exists():
            raise WorkflowError("Publication target already exists; history is never overwritten.")
        try:
            staging.rename(destination)
            return
        except PermissionError as error:
            if getattr(error, "winerror", None) not in (5, 32, 33) or attempt == 3:
                raise
            time.sleep(delay)


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,100}", value):
        raise WorkflowError("Identifiers must contain letters, digits, underscores or hyphens.")
    return value


def inside(root, relative):
    if Path(relative).is_absolute() or ".." in Path(relative).parts or ":" in str(relative):
        raise WorkflowError(f"Expected a relative path without parent traversal: {relative}")
    candidate = root / relative
    no_links(candidate)
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise WorkflowError(f"Path leaves project directory: {relative}")
    return candidate


def no_links(path):
    """Do not follow a symlink/junction even when it points back inside a root."""
    for part in (Path(path), *Path(path).parents):
        try:
            reparse = getattr(part.lstat(), "st_file_attributes", 0) & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
        except FileNotFoundError:
            reparse = False
        if part.is_symlink() or getattr(part, "is_junction", lambda: False)() or reparse:
            raise WorkflowError(f"Linked workflow paths are not supported: {part.name}")


def safe_name(value):
    if not isinstance(value, str) or not value:
        raise WorkflowError("A nonempty project/file name is required.")
    name = unicodedata.normalize("NFC", value.strip())
    reserved = {"CON", "PRN", "AUX", "NUL", "CLOCK$", "CONIN$", "CONOUT$"}
    reserved |= {p + str(n) for p in ("COM", "LPT") for n in range(1, 10)}
    reserved |= {p + n for p in ("COM", "LPT") for n in "¹²³"}
    if (not name or name in (".", "..") or name.endswith((".", " "))
            or re.search(r'[\\/:*?"<>|\x00-\x1f\x7f]', name)
            or name.split(".")[0].upper() in reserved
            or len(name.encode("utf-16-le")) > 160):
        raise WorkflowError("Unsafe or overly long project/file name; choose a distinct Windows-safe name.")
    return name


def inventory(folder):
    if not folder.is_dir():
        raise WorkflowError(f"Missing directory: {folder}")
    if folder.is_symlink() or getattr(folder, "is_junction", lambda: False)():
        raise WorkflowError("Linked snapshot root is not supported.")
    found = {}
    for path in sorted(folder.rglob("*")):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise WorkflowError(f"Linked files/directories are not snapshot inputs: {path.name}")
        if path.is_file():
            found[path.relative_to(folder).as_posix()] = digest(path.read_bytes())
    return found


@contextmanager
def locked(root):
    no_links(root / ".workflow.lock")
    lock = root / ".workflow.lock"
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError:
        raise WorkflowError("Another state operation is running. A stale lock requires verifying its process has stopped.")
    with stream:
        stream.write(json.dumps({"pid": os.getpid(), "started": now()}))
    try:
        yield
    finally:
        lock.unlink()


def state_at(root):
    no_links(root / "state.json")
    state = read_json(root / "state.json")
    if state.get("schema_version") != 1:
        raise WorkflowError("Unsupported project state schema.")
    return state


def discover(root):
    """Read only bounded project metadata, never choose between client matters."""
    if not root.is_dir():
        raise WorkflowError("Project directory does not exist.")
    candidates = [root]
    matters = root / "matters"
    if matters.is_dir() and not matters.is_symlink() and not getattr(matters, "is_junction", lambda: False)():
        candidates.extend(sorted(p for p in matters.iterdir() if p.is_dir()))
    found, errors = [], []
    for candidate in candidates:
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            continue
        path = candidate / "state.json"
        if not path.is_file():
            continue
        try:
            inside(root, str(path.relative_to(root)))
            state = state_at(candidate)
            found.append({"root": str(candidate.resolve()), "matter_id": state["matter_id"],
                          "project_name": state.get("project_name_display"),
                          "head": state["head"], "status": current_status(state),
                          "history_verified": False})
        except (OSError, ValueError, KeyError, TypeError) as error:
            errors.append({"root": str(candidate), "error": str(error)})
    return {"matters": found, "errors": errors, "selection_required": len(found) != 1 or bool(errors),
            "note": "Metadata only. Confirm the matter matches the request before reading its content; use status to verify history."}


def markdown_footnotes(text):
    """Check ordinary Markdown footnotes; not a renderer or legal verifier."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    definitions, body = [], []
    fence = None
    in_definition = False
    for line in text.splitlines():
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if fence:
            if re.fullmatch(re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", stripped):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        definition = re.match(r"^ {0,3}\[\^([^\]\s]+)\]:", line)
        if definition:
            definitions.append(definition.group(1))
            in_definition = True
            continue
        if in_definition and (not stripped or line.startswith(("    ", "\t"))):
            continue
        in_definition = False
        body.append(line)
    prose = re.sub(r"(`+).*?\1", "", "\n".join(body))
    references = set(re.findall(r"(?<!\\)\[\^([^\]\s]+)\]", prose))
    defined = set(definitions)
    return {"undefined": sorted(references - defined), "unused": sorted(defined - references),
            "duplicates": sorted(key for key in defined if definitions.count(key) > 1)}


def check_pair(root, verification, clean, common_start=None, common_end=None):
    if bool(common_start) != bool(common_end):
        raise WorkflowError("Supply both common-start and common-end, or neither.")
    paths = {"verification": inside(root, verification), "clean": inside(root, clean)}
    if paths["verification"].resolve() == paths["clean"].resolve():
        raise WorkflowError("Two distinct view files are required.")
    result = {"files": {}, "common_body": "NOT_CHECKED", "legal_review": "NOT_PERFORMED",
              "limitations": ["Footnote checks support ordinary Markdown, not rendered pages or legal correctness."]}
    texts = {}
    for view, path in paths.items():
        data = path.read_bytes()
        record = {"path": str(path.resolve()), "sha256": digest(data)}
        if path.suffix.lower() == ".md":
            texts[view] = data.decode("utf-8-sig")
            record["footnotes"] = markdown_footnotes(texts[view])
        else:
            record["footnotes"] = "NOT_SUPPORTED"
        result["files"][view] = record
    if common_start and len(texts) == 2:
        bodies = []
        for view in ("verification", "clean"):
            text = texts[view]
            if text.count(common_start) != 1 or text.count(common_end) != 1:
                raise WorkflowError("Common body boundaries must each appear exactly once in both views.")
            start = text.index(common_start) + len(common_start)
            end = text.index(common_end)
            if end <= start or not text[start:end].strip():
                raise WorkflowError("Common body must be nonempty and end after its start.")
            bodies.append(text[start:end].replace("\r\n", "\n"))
        result["common_body"] = "IDENTICAL" if bodies[0] == bodies[1] else "DIFFERENT"
    else:
        result["limitations"].append("Common body not compared: provide explicit unique boundaries for both Markdown views or compare manually.")
    return result


def checked_version(root, state, version):
    if version not in state["versions"]:
        raise WorkflowError(f"Unknown version: {version}")
    folder = root / "versions" / version
    no_links(folder)
    registration = state["versions"][version]
    if digest((folder / "manifest.json").read_bytes()) != registration["manifest_sha256"]:
        raise WorkflowError(f"Version manifest changed: {version}")
    manifest = read_json(folder / "manifest.json")
    if inventory(folder / "files") != manifest["files"]:
        raise WorkflowError(f"Submitted files changed: {version}. Preserve history; create a new submission.")
    if digest((folder / "CHANGES.md").read_bytes()) != manifest["changes_sha256"]:
        raise WorkflowError(f"Version comparison changed: {version}")
    return manifest


def checked_review(root, review_id, record):
    no_links(root / "reviews" / review_id)
    if record["status"] == "complete":
        if inventory(root / "reviews" / review_id / "final") != record["files"]:
            raise WorkflowError(f"Completed review changed: {review_id}")


def verify_history(root, state):
    for version in state["versions"]:
        checked_version(root, state, version)
    for review_id, record in state["reviews"].items():
        checked_review(root, review_id, record)
    for release_id, record in state.get("releases", {}).items():
        release_record(root, release_id, record)


def effective_reviews(state, version=None):
    version = version or state["head"]
    records = [(key, value) for key, value in state["reviews"].items()
               if value["version"] == version]
    superseded = {key for _, record in records if record["status"] == "complete"
                  for key in record.get("supersedes", [])}
    return [(key, value) for key, value in records if key not in superseded]


def inherited_blockers(root, state, version):
    chain = []
    ancestor = state["versions"][version]["parent"]
    while ancestor:
        if ancestor in chain:
            raise WorkflowError("Cyclic version history.")
        chain.append(ancestor)
        ancestor = state["versions"][ancestor]["parent"]
    blockers = set()
    for ancestor in reversed(chain):
        findings = {}
        for rid, record in effective_reviews(state, ancestor):
            if record["status"] == "complete":
                for finding in read_json(root / "reviews" / rid / "final/result.json")["findings"]:
                    findings.setdefault(finding["id"], []).append(finding)
        for fid, decisions in findings.items():
            if any(f["blocking"] and f["status"] == "OPEN" for f in decisions):
                blockers.add(fid)
            elif all(f["status"] == "RESOLVED" for f in decisions):
                blockers.discard(fid)
    return blockers


def current_status(state):
    if state["head"] is None:
        return "NO_SUBMISSION"
    reviews = effective_reviews(state)
    if any(r["status"] == "open" for _, r in reviews):
        return "IN_REVIEW"
    completed = [r for _, r in reviews if r["status"] == "complete"]
    if not completed:
        return "AWAITING_REVIEW"
    if any(r["verdict"] == "PENDING" for r in completed):
        return "PENDING"
    if any(r["verdict"] == "REVISE" for r in completed):
        return "REVISE"
    return "PASS"


def render_work(state):
    status = current_status(state)
    next_step = {
        "NO_SUBMISSION": "启动生成对话，形成并提交首版双文件。",
        "AWAITING_REVIEW": "启动独立审阅对话，直接读取当前版本。",
        "IN_REVIEW": "由已启动的审阅对话完成检查并写入独立意见。",
        "REVISE": "启动生成对话，读取下列完整审阅意见，修订后提交新版本。",
        "PENDING": "读取审阅报告中的具体补件／确认事项，完成可处理部分。",
        "PASS": "当前版本审阅通过，停止修订循环；正式交付仍按技能要求取得律师确认。",
    }[status]
    lines = ["# 项目工作记录", "", "> 程序生成的索引；完整文稿和意见以链接文件为准。请勿手工覆盖。", "",
             f"- 事项：{state['matter_id']}", f"- 登记序号：{state['revision']}",
             f"- 当前版本：{state['head'] or '尚未提交'}", f"- 当前审阅状态：{status}",
             f"- 下一步：{next_step}", "", "## 当前双文件", ""]
    if state["head"]:
        head = state["head"]
        pair = state["versions"][head]["pair"]
        for label, key in (("核验草稿", "verification"), ("纯净展示", "clean")):
            lines.append(f"- [{label}](versions/{head}/files/{pair[key]})")
        lines.append(f"- [版本差异](versions/{head}/CHANGES.md)")
        for item in state["versions"][head].get("deliverables", []):
            lines.append(f"- {item['title']}：[{item['id']} 正文](versions/{head}/files/{item['clean']}) / [核验稿](versions/{head}/files/{item['verification']})")
    lines += ["", "## 审阅记录（保留历史）", ""]
    for rid, record in state["reviews"].items():
        historical = "当前版本" if record["version"] == state["head"] else "历史版本，不能批准当前稿"
        verdict = record.get("verdict", "已取消" if record["status"] == "cancelled" else "进行中")
        location = "final/REVIEW.md" if record["status"] == "complete" else "REVIEW.md"
        lines.append(f"- [{rid}](reviews/{rid}/{location})：{record['version']} / {verdict} / {historical}")
        if record.get("supersedes"):
            lines.append("  - 明确替代的旧审阅：" + ", ".join(record["supersedes"]))
    lines += ["", "## 版本历史", ""]
    for version, record in state["versions"].items():
        lines.append(f"- [{version}](versions/{version}/manifest.json)：基线 {record['parent'] or '首稿'}；{record['created_at']}")
    lines += ["", "## 正式交付记录", ""]
    for release_id, record in state.get("releases", {}).items():
        lines.append(f"- [{release_id}](releases/{release_id}/request.json)：{record['version']} / {record['status']}")
    lines += ["", "最新送审版与最近正式交付版分别记录；文件共享不会自动唤醒下一对话。", ""]
    return "\n".join(lines).encode("utf-8")


def save_state(root, state, event):
    state["revision"] += 1
    state["events"].append({"time": now(), **event})
    atomic_write(root / "state.json", json_bytes(state))
    # If this derived index fails, state.json remains the authoritative commit.
    # `status` can reconstruct WORK.md after filesystem availability is restored.
    atomic_write(root / "WORK.md", render_work(state))


def init_project(root, matter_id):
    identifier(matter_id)
    no_links(root)
    if root.exists() and any(root.iterdir()):
        raise WorkflowError("Initialize in a new or empty matter directory; existing files are never overwritten.")
    if not (TEMPLATES / "PROJECT.md").is_file():
        raise WorkflowError("Project templates unavailable. Use the original project kit to initialize.")
    root.mkdir(parents=True, exist_ok=True)
    no_links(root)
    for name in ("inputs", "drafts", "versions", "reviews", "releases"):
        (root / name).mkdir()
    for name in ("AGENTS.md", "PROJECT.md"):
        shutil.copyfile(TEMPLATES / name, root / name)
    state = {"schema_version": 1, "matter_id": matter_id, "revision": 0,
             "runtime_version": RUNTIME_VERSION, "head": None, "versions": {}, "reviews": {}, "events": [], "releases": {}}
    with locked(root):
        save_state(root, state, {"action": "init"})
    return {"root": str(root), "status": "NO_SUBMISSION"}


def checkout(root, actor, from_version=None):
    identifier(actor)
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        source = from_version or state["head"]
        draft_id = f"{actor}-{uuid.uuid4().hex[:12]}"
        destination = root / "drafts" / draft_id
        destination.mkdir()
        if source:
            checked_version(root, state, source)
            shutil.copytree(root / "versions" / source / "files", destination / "files")
        else:
            (destination / "files" / "evidence").mkdir(parents=True)
        metadata = {"actor": actor, "base": state["head"], "content_from": source, "created_at": now()}
        atomic_write(destination / "draft.json", json_bytes(metadata))
        save_state(root, state, {"action": "checkout", "draft": draft_id, "actor": actor})
    return {"draft": draft_id, "files": str(destination / "files"), "base": metadata["base"]}


def next_id(folder, prefix):
    numbers = [int(p.name[len(prefix):]) for p in folder.iterdir()
               if re.fullmatch(re.escape(prefix) + r"\d+", p.name)]
    return f"{prefix}{max(numbers, default=0) + 1:04d}"


def difference(old_folder, new_folder):
    previous = inventory(old_folder) if old_folder else {}
    current = inventory(new_folder)
    sections = ["# 本次版本差异", "", "文本差异由本地程序计算，不能替代语义和页面审阅。", ""]
    for name in sorted(set(previous) | set(current)):
        if previous.get(name) == current.get(name):
            continue
        sections += [f"## {name}", ""]
        before = (old_folder / name).read_bytes() if name in previous else b""
        after = (new_folder / name).read_bytes() if name in current else b""
        try:
            if Path(name).suffix.lower() not in TEXT_SUFFIXES:
                raise UnicodeError()
            delta = "\n".join(difflib.unified_diff(before.decode("utf-8-sig").splitlines(),
                         after.decode("utf-8-sig").splitlines(), fromfile="上一版本", tofile="本版本", lineterm=""))
            fence = "`" * max(3, max((len(m.group()) for m in re.finditer(r"`+", delta)), default=0) + 1)
            sections += [fence + "diff", delta, fence, ""]
        except UnicodeError:
            sections += ["文件字节已变化；未计算该格式的文字／原生修订差异，请按需比较文档并核验页面。", ""]
    return ("\n".join(sections) + "\n").encode("utf-8")


def submit(root, draft_id, verification=None, clean=None, deliverables=None, execution_ref=None):
    identifier(draft_id)
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        draft = root / "drafts" / draft_id
        metadata = read_json(draft / "draft.json")
        if metadata["base"] != state["head"]:
            raise WorkflowError("Submission base is stale. Read the new version and integrate in a fresh draft.")
        files = draft / "files"
        package = None
        if deliverables:
            package = validate_deliverables(files, read_json(inside(files, deliverables)))
            if not isinstance(execution_ref, str) or not execution_ref.strip():
                raise WorkflowError("Managed submissions require the actual generation execution-ref.")
            primary = next(item for item in package["deliverables"] if item["id"] == package["primary"])
            verification, clean = primary["verification"], primary["clean"]
        if not verification or not clean:
            raise WorkflowError("Supply a deliverables manifest or both verification and clean files.")
        verification, clean = Path(verification).as_posix(), Path(clean).as_posix()
        if inside(files, verification).resolve() == inside(files, clean).resolve():
            raise WorkflowError("Two distinct view files are required.")
        for required in (verification, clean, "BRIEF.md", "RESPONSE.md"):
            path = inside(files, required)
            if not path.is_file() or not path.read_bytes().strip():
                raise WorkflowError(f"Missing or empty submission file: {required}")
        original = inventory(files)
        version = next_id(root / "versions", "v")
        staging = root / "versions" / f".pending-{uuid.uuid4().hex}"
        staging.mkdir()
        shutil.copytree(files, staging / "files")
        if original != inventory(files) or original != inventory(staging / "files"):
            raise WorkflowError("Draft changed during copying. No submission registered; retry after editing stops.")
        parent = state["head"]
        changes = difference(root / "versions" / parent / "files" if parent else None, staging / "files")
        (staging / "CHANGES.md").write_bytes(changes)
        manifest = {"version": version, "parent": parent, "content_from": metadata["content_from"],
                    "actor": metadata["actor"], "created_at": now(),
                    "pair": {"verification": Path(verification).as_posix(), "clean": Path(clean).as_posix()},
                    "files": original, "changes_sha256": digest(changes)}
        if package:
            manifest.update(package, submission_protocol=2, generation_execution_ref=execution_ref)
        manifest_data = json_bytes(manifest)
        (staging / "manifest.json").write_bytes(manifest_data)
        publish_directory(staging, root / "versions" / version)
        state["versions"][version] = {k: manifest[k] for k in ("parent", "actor", "pair", "created_at")}
        state["versions"][version]["manifest_sha256"] = digest(manifest_data)
        if package:
            state["versions"][version]["deliverables"] = package["deliverables"]
        state["head"] = version
        save_state(root, state, {"action": "submit", "version": version, "draft": draft_id})
    return {"version": version, "status": "AWAITING_REVIEW"}


def start_review(root, actor, version=None):
    identifier(actor)
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        version = version or state["head"]
        manifest = checked_version(root, state, version)
        if actor == manifest["actor"]:
            raise WorkflowError("The generating actor cannot register its own independent review.")
        rid = next_id(root / "reviews", "r")
        folder = root / "reviews" / rid
        folder.mkdir()
        protocol = 3 if manifest.get("submission_protocol") == 2 else 2
        result = {"version": version, "review_protocol": protocol, "summary": "", "execution_ref": "",
                  "checks": {key: {"status": "PENDING", "evidence": ""} for key in CHECKS},
                  "findings": [], "unperformed_checks": [], "supersedes": [], "supersedes_reason": ""}
        if protocol == 3:
            result.update(scope="pending", reviewed_deliverables=[],
                          independence={"status": "unverified", "generation_ref": manifest["generation_execution_ref"], "review_ref": ""},
                          pages={"status": "PENDING", "evidence": ""})
        (folder / "result.json").write_bytes(json_bytes(result))
        (folder / "REVIEW.md").write_text("", encoding="utf-8")
        state["reviews"][rid] = {"version": version, "review_protocol": protocol, "actor": actor, "status": "open", "started_at": now(),
                                  "manifest_sha256": state["versions"][version]["manifest_sha256"]}
        save_state(root, state, {"action": "start-review", "review": rid, "version": version})
    return {"review": rid, "directory": str(folder), "version": version}


def validate_result(root, state, record, result):
    version = record["version"]
    if result.get("review_protocol", 1) != record.get("review_protocol", 1):
        raise WorkflowError("Review protocol cannot change after review registration.")
    if result.get("version") != version:
        raise WorkflowError("Review result is for a different version.")
    for field in ("summary", "execution_ref"):
        if not isinstance(result.get(field), str) or not result[field].strip():
            raise WorkflowError(f"Review requires a real {field}.")
    checks = result.get("checks", {})
    if set(checks) != set(CHECKS):
        raise WorkflowError("All four review dimensions are required.")
    for check in checks.values():
        if check.get("status") not in ("PASS", "REVISE", "PENDING") or not str(check.get("evidence", "")).strip():
            raise WorkflowError("Each dimension requires its status and evidence/limitation description.")
    findings = result.get("findings")
    gaps = result.get("unperformed_checks")
    supersedes = result.get("supersedes")
    if not all(isinstance(value, list) for value in (findings, gaps, supersedes)):
        raise WorkflowError("findings, unperformed_checks and supersedes must be lists.")
    manifest = checked_version(root, state, version)
    if result.get("review_protocol", 1) >= 3:
        if result.get("scope") not in ("full", "limited"):
            raise WorkflowError("State the actual review scope: full or limited.")
        known = {item["id"] for item in manifest["deliverables"]}
        reviewed = result.get("reviewed_deliverables")
        if not isinstance(reviewed, list) or not reviewed or not set(reviewed) <= known:
            raise WorkflowError("Identify the deliverables actually reviewed.")
        if result["scope"] == "full" and set(reviewed) != known:
            raise WorkflowError("A full review must cover every deliverable in the submitted package.")
        pages = result.get("pages", {})
        if pages.get("status") not in ("PASS", "PENDING", "NOT_REQUIRED") or not str(pages.get("evidence", "")).strip():
            raise WorkflowError("Record actual page inspection or why it is not required.")
    seen = set()
    for finding in findings:
        fid = identifier(finding["id"])
        if fid in seen:
            raise WorkflowError(f"Duplicate finding identifier: {fid}")
        seen.add(fid)
        if type(finding.get("blocking")) is not bool or finding.get("status") not in ("OPEN", "RESOLVED"):
            raise WorkflowError("Findings require blocking boolean and OPEN/RESOLVED status.")
        for field in ("reason", "requested_change", "acceptance"):
            if not isinstance(finding.get(field), str) or not finding[field].strip():
                raise WorkflowError(f"Finding requires {field}.")
        if result.get("review_protocol", 1) >= 2:
            if finding.get("kind") not in ("error", "unverified", "preference"):
                raise WorkflowError("Finding requires kind: error, unverified or preference.")
            if not isinstance(finding.get("basis"), str) or not finding["basis"].strip():
                raise WorkflowError("Finding requires basis: actual source/passage and applicability, or the precise missing evidence.")
            if finding["kind"] == "preference" and finding["blocking"]:
                raise WorkflowError("An optional preference cannot block review.")
            if finding["status"] == "RESOLVED" and not str(finding.get("resolution", "")).strip():
                raise WorkflowError("Resolved findings require a reviewer's evidence and reason, including withdrawn mistakes.")
        anchor = finding.get("anchor", {})
        if anchor.get("version") != version or anchor.get("file") not in review_files(manifest):
            raise WorkflowError("Finding must target one view file in the reviewed version.")
        if anchor.get("scope") == "document":
            continue
        if not anchor.get("exact") or not anchor.get("section"):
            raise WorkflowError("Text findings require exact quotation and section (or document scope).")
        if Path(anchor["file"]).suffix.lower() in TEXT_SUFFIXES:
            text = inside(root / "versions" / version / "files", anchor["file"]).read_text(encoding="utf-8-sig")
            quote = anchor.get("prefix", "") + anchor["exact"] + anchor.get("suffix", "")
            if text.count(quote) != 1:
                raise WorkflowError("Quotation not uniquely located; supply matching context or relocate it.")
    for old in supersedes:
        prior = state["reviews"].get(old)
        if not prior or prior["version"] != version or prior["status"] != "complete":
            raise WorkflowError("Only completed reviews of the same version may be explicitly superseded.")
    if supersedes and not result.get("supersedes_reason", "").strip():
        raise WorkflowError("Superseding a review requires an explicit reason; historical files remain intact.")
    statuses = [check["status"] for check in checks.values()]
    if result.get("review_protocol", 1) >= 3 and result["scope"] == "full":
        current_findings = {f["id"]: f for f in findings}
        for fid in inherited_blockers(root, state, version):
            if fid not in current_findings:
                raise WorkflowError(f"Inherited blocking finding {fid} needs an explicit new-version disposition.")
            disposition = current_findings[fid]
            if (disposition["status"] == "RESOLVED" or not disposition["blocking"]) and not disposition.get("resolution", "").strip():
                raise WorkflowError("Closing or downgrading an inherited blocker requires the reviewer's reason and evidence.")
    if result.get("review_protocol", 1) >= 3 and result["pages"]["status"] == "PENDING":
        return "PENDING"
    if result.get("review_protocol", 1) >= 3:
        if result["scope"] != "full" or result.get("independence", {}).get("status") != "separate_conversation":
            return "PENDING"
        if any(d["page_check_required"] for d in manifest["deliverables"]) and result["pages"]["status"] != "PASS":
            return "PENDING"
    if "PENDING" in statuses or gaps or any(f.get("kind") == "unverified" and f["blocking"] and f["status"] == "OPEN" for f in findings):
        return "PENDING"
    if "REVISE" in statuses or any(f["blocking"] and f["status"] == "OPEN" for f in findings):
        return "REVISE"
    return "PASS"


def finish_review(root, rid):
    identifier(rid)
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        record = state["reviews"].get(rid)
        if not record or record["status"] != "open":
            raise WorkflowError("Review is not open; completed reviews are never overwritten.")
        folder = root / "reviews" / rid
        report = (folder / "REVIEW.md").read_bytes()
        raw_result = (folder / "result.json").read_bytes()
        if not report.strip():
            raise WorkflowError("Write the actual review report before finalizing.")
        result = json.loads(raw_result.decode("utf-8-sig"))
        verdict = validate_result(root, state, record, result)
        if record["manifest_sha256"] != state["versions"][record["version"]]["manifest_sha256"]:
            raise WorkflowError("Review target changed.")
        staging = folder / f".pending-{uuid.uuid4().hex}"
        staging.mkdir()
        (staging / "REVIEW.md").write_bytes(report)
        (staging / "result.json").write_bytes(raw_result)
        if report != (folder / "REVIEW.md").read_bytes() or raw_result != (folder / "result.json").read_bytes():
            raise WorkflowError("Review edited during finalization; no result registered.")
        if (folder / "final").exists():
            raise WorkflowError("Unregistered final directory exists; inspect interrupted operation before recovery.")
        publish_directory(staging, folder / "final")
        record.update(status="complete", verdict=verdict, completed_at=now(),
                      files=inventory(folder / "final"), supersedes=result["supersedes"])
        save_state(root, state, {"action": "finish-review", "review": rid, "verdict": verdict})
    return {"review": rid, "verdict": verdict, "current_status": current_status(state),
            "historical": record["version"] != state["head"]}


def status(root):
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        atomic_write(root / "WORK.md", render_work(state))
    return {"head": state["head"], "status": current_status(state), "revision": state["revision"],
            "last_published_version": state.get("last_published_version"),
            "last_published_release": state.get("last_published_release")}


def cancel_review(root, rid, reason):
    identifier(rid)
    if not reason.strip():
        raise WorkflowError("Cancelling an abandoned review requires a reason.")
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        record = state["reviews"].get(rid)
        if not record or record["status"] != "open":
            raise WorkflowError("Only an open review can be cancelled; completed results remain historical records.")
        record.update(status="cancelled", cancelled_at=now(), cancellation_reason=reason)
        save_state(root, state, {"action": "cancel-review", "review": rid, "reason": reason})
    return {"review": rid, "status": "cancelled", "current_status": current_status(state)}


def validate_deliverables(files, data):
    if not isinstance(data, dict) or not isinstance(data.get("deliverables"), list) or not data["deliverables"]:
        raise WorkflowError("A nonempty deliverables list is required.")
    seen, paths = set(), set()
    for item in data["deliverables"]:
        item_id = identifier(item["id"])
        if item_id in seen:
            raise WorkflowError("Duplicate deliverable identifier.")
        seen.add(item_id)
        for field in ("title", "purpose", "verification", "clean"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise WorkflowError(f"Deliverable requires {field}.")
        if type(item.get("page_check_required")) is not bool:
            raise WorkflowError("Declare page_check_required for each deliverable.")
        for field in ("verification", "clean"):
            path = inside(files, item[field])
            normalized = str(path.resolve()).casefold()
            if normalized in paths or not path.is_file() or not path.read_bytes().strip():
                raise WorkflowError("Deliverable views must be distinct, nonempty files.")
            paths.add(normalized)
            item[field] = Path(item[field]).as_posix()
        validate_artifact(inside(files, item["clean"]))
    if data.get("primary") not in seen:
        raise WorkflowError("Select a primary deliverable from the submitted list.")
    for item in data["deliverables"]:
        related = item.get("related", [])
        if not isinstance(related, list) or not set(related) <= seen:
            raise WorkflowError("Related deliverables must exist in the same package.")
    return {"primary": data["primary"], "deliverables": data["deliverables"]}


def validate_artifact(path):
    """Structural checks only; legal/semantic/page checks remain actual review work."""
    if not path.is_file() or not path.stat().st_size:
        raise WorkflowError("Missing or empty delivery candidate.")
    if path.suffix.lower() == ".docx":
        try:
            with ZipFile(path) as archive:
                if archive.testzip() or not {"[Content_Types].xml", "word/document.xml"} <= set(archive.namelist()):
                    raise WorkflowError("Invalid Word candidate.")
                ET.fromstring(archive.read("word/document.xml"))
        except (BadZipFile, ET.ParseError, KeyError) as error:
            raise WorkflowError("Invalid Word candidate; regenerate before submission.") from error
    elif path.suffix.lower() == ".pdf" and not path.read_bytes().startswith(b"%PDF-"):
        raise WorkflowError("Invalid PDF candidate.")


def review_files(manifest):
    return set(manifest["files"]) if manifest.get("submission_protocol") == 2 else set(manifest["pair"].values())


def bind_matter(workspace, actor, role, matter=None, create=False, new=False, project_name=None):
    """Bind each real conversation separately; never use a global active matter."""
    identifier(actor)
    if role not in ("generation", "review"):
        raise WorkflowError("Role must be generation or review.")
    no_links(workspace)
    with locked(workspace):
        registry_dir = inside(workspace, ".lexprism")
        registry = inside(workspace, ".lexprism/bindings.json")
        bindings = read_json(registry) if registry.exists() else {}
        if actor in bindings and bindings[actor]["role"] != role:
            raise WorkflowError("This window has a different bound role; use the actual separate review window.")
        discovered = discover(workspace)
        if discovered["errors"]:
            raise WorkflowError("Invalid matter metadata found; inspect it instead of creating a replacement.")
        selected = None
        if matter and new:
            raise WorkflowError("Choose an existing matter or request a new one, not both.")
        if matter:
            p = Path(matter)
            if p.is_absolute():
                no_links(p)
                if not p.resolve().is_relative_to(workspace.resolve()):
                    raise WorkflowError("Matter is outside the authorized workspace.")
                selected = p
            else:
                selected = inside(workspace, matter)
        elif not new and actor in bindings and not project_name:
            if bindings[actor]["role"] != role:
                raise WorkflowError("This conversation is bound to a different role; use the actual separate conversation.")
            selected = inside(workspace, bindings[actor]["matter"])
        elif not new:
            matches = discovered["matters"]
            if project_name:
                matches = [m for m in matches if m.get("project_name") == project_name]
            if len(matches) == 1:
                selected = Path(matches[0]["root"])
            elif matches or discovered["matters"]:
                return {**discovered, "selection_required": True, "bound": False}
        if selected is None:
            if role != "generation" or not (create or new):
                return {**discovered, "selection_required": True, "bound": False}
            if project_name and any(m.get("project_name") == project_name for m in discovered["matters"]):
                return {**discovered, "selection_required": True, "bound": False}
            if project_name:
                safe_name(project_name)
            selected = inside(workspace, "matters/m-" + uuid.uuid4().hex[:16])
            init_project(selected, selected.name)
            if project_name:
                st = state_at(selected)
                st["project_name_display"] = project_name
                save_state(selected, st, {"action": "initial-name", "name": project_name, "confirmed_for_release": False})
        if not any(Path(m["root"]).resolve() == selected.resolve() for m in discovered["matters"]) and not (create or new):
            raise WorkflowError("Selected matter is not registered in this workspace.")
        state = state_at(selected)
        verify_history(selected, state)
        registry_dir.mkdir(exist_ok=True)
        bindings[actor] = {"matter": selected.relative_to(workspace).as_posix(), "role": role, "bound_at": now()}
        atomic_write(registry, json_bytes(bindings))
        return {"bound": True, "root": str(selected.resolve()), "matter_id": state["matter_id"],
                "head": state["head"], "status": current_status(state), "role": role,
                "identity": "recorded conversation reference, not host authentication"}


def release_record(root, release_id, record):
    identifier(release_id)
    folder = inside(root, f"releases/{release_id}")
    request_data = (folder / "request.json").read_bytes()
    if digest(request_data) != record["request_sha256"]:
        raise WorkflowError("Release request changed; preserve the original confirmation scope.")
    request = json.loads(request_data)
    if record.get("confirmation_sha256"):
        raw = (folder / "confirmation.json").read_bytes()
        if digest(raw) != record["confirmation_sha256"]:
            raise WorkflowError("Lawyer confirmation record changed.")
        confirmation = json.loads(raw)
        if confirmation.get("request_sha256") != record["request_sha256"]:
            raise WorkflowError("Confirmation is bound to a different release request.")
    return request


def release_readiness(root, state):
    verify_history(root, state)
    if current_status(state) != "PASS":
        raise WorkflowError("The latest version must have effective PASS reviews and no open review.")
    manifest = checked_version(root, state, state["head"])
    if manifest.get("submission_protocol") != 2:
        raise WorkflowError("Legacy history remains readable. Submit a managed deliverables package before formal release.")
    generation_ref = manifest["generation_execution_ref"]
    records = {}
    for rid, review in effective_reviews(state):
        if review["status"] != "complete":
            continue
        result = read_json(root / "reviews" / rid / "final/result.json")
        if result.get("scope") != "full" or set(result.get("reviewed_deliverables", [])) != {d["id"] for d in manifest["deliverables"]}:
            raise WorkflowError("Formal release requires full review of the current deliverables package.")
        independence = result.get("independence", {})
        if (independence.get("status") != "separate_conversation"
                or independence.get("generation_ref") != generation_ref
                or not independence.get("review_ref")
                or independence["review_ref"] != result["execution_ref"]
                or independence["review_ref"] == generation_ref):
            raise WorkflowError("An actual separate-conversation review reference is required; actor names alone are insufficient.")
        if any(d["page_check_required"] for d in manifest["deliverables"]) and result.get("pages", {}).get("status") != "PASS":
            raise WorkflowError("Required page inspection is incomplete.")
        if validate_result(root, state, review, result) != "PASS":
            raise WorkflowError("Necessary checks or blocking findings remain unfinished.")
        records[rid] = review["files"]
    if not records:
        raise WorkflowError("No completed independent review covers this version.")
    return manifest, digest(json_bytes(records))


def output_registry(workspace):
    path = inside(workspace, ".lexprism/output-owners.json")
    return path, read_json(path) if path.exists() else {}


def output_target(root, workspace, request, owners, release_id=None):
    no_links(workspace)
    if not root.resolve().is_relative_to(workspace.resolve()) or root.resolve() == workspace.resolve():
        raise WorkflowError("Release requires a matter inside its explicit authorized workspace.")
    name = safe_name(request["output_dir_name"])
    output = inside(workspace, "output")
    folder = inside(workspace, "output/" + name)
    if output.exists() and not output.is_dir():
        raise WorkflowError("Output root is not a directory.")
    if output.is_dir():
        for child in output.iterdir():
            if child.name.casefold() == name.casefold() and child.name != name:
                raise WorkflowError("Output directory has a case-equivalent name; confirm a distinct name.")
    owner = owners.get(name.casefold())
    relative = root.relative_to(workspace).as_posix()
    if owner and (owner["matter"] != relative or owner["matter_id"] != state_at(root)["matter_id"]):
        raise WorkflowError("Output directory belongs to another matter.")
    if folder.exists() and (not folder.is_dir() or not owner):
        raise WorkflowError("Output directory ownership is unknown; choose a distinct project name.")
    for item in request["files"]:
        filename = safe_name(item["output_name"])
        target = inside(workspace, "output/" + name + "/" + filename)
        if len(str(target)) > 240:
            raise WorkflowError("Output path is too long; choose shorter project/file names or workspace path.")
        if folder.exists():
            if any(p.name.casefold() == filename.casefold() and p.name != filename for p in folder.iterdir()):
                raise WorkflowError("A case-equivalent output file already exists.")
        reservation = owner.get("files", {}).get(filename.casefold()) if owner else None
        if reservation and (reservation.get("release_id") != release_id or reservation.get("sha256") != item["sha256"]):
            raise WorkflowError("Output filename is already reserved by a different release.")
        if target.exists() and (not reservation or not release_id or not target.is_file() or digest(target.read_bytes()) != item["sha256"]):
            raise WorkflowError("Existing output is not this release's verified file; never overwrite it.")
    return folder


def prepare_release(root, workspace, project_name=None, file_name=None, selected=None):
    no_links(workspace)
    with locked(root), locked(workspace):
        state = state_at(root)
        manifest, reviews_hash = release_readiness(root, state)
        display = project_name or state.get("project_name_display")
        dirname = safe_name(display)
        selected = selected or [manifest["primary"]]
        items = {d["id"]: d for d in manifest["deliverables"]}
        if not selected or len(selected) != len(set(selected)) or not set(selected) <= set(items):
            raise WorkflowError("Select distinct deliverables from the current package.")
        if file_name and len(selected) != 1:
            raise WorkflowError("A custom file name is for one selected deliverable; otherwise use each deliverable title.")
        outputs = []
        for did in selected:
            item = items[did]
            candidate = inside(root, f"versions/{state['head']}/files/{item['clean']}")
            validate_artifact(candidate)
            ext = candidate.suffix.lower()
            if ext not in (".docx", ".pdf", ".md", ".txt"):
                raise WorkflowError("Delivery candidate must be an editable document, PDF or explicitly requested text file.")
            label = file_name or item["title"]
            if Path(label).suffix.lower() in (".docx", ".pdf", ".md", ".txt"):
                if Path(label).suffix.lower() != ext:
                    raise WorkflowError("Changing format requires a new reviewed candidate, not a filename extension change.")
                label = str(Path(label).with_suffix(""))
            output_name = safe_name(f"{safe_name(label)}_{state['head']}{ext}")
            outputs.append({"deliverable": did, "source": item["clean"], "sha256": digest(candidate.read_bytes()), "output_name": output_name})
        if len({item["output_name"].casefold() for item in outputs}) != len(outputs):
            raise WorkflowError("Selected deliverables have colliding filenames; use distinct titles.")
        request = {"version": state["head"], "manifest_sha256": state["versions"][state["head"]]["manifest_sha256"],
                   "reviews_sha256": reviews_hash, "workspace": str(workspace.resolve()),
                   "project_name_display": display, "output_dir_name": dirname, "files": outputs, "created_at": now()}
        _, owners = output_registry(workspace)
        folder = output_target(root, workspace, request, owners)
        rid = "release-" + uuid.uuid4().hex[:16]
        destination = inside(root, f"releases/{rid}")
        destination.mkdir(parents=True)
        raw = json_bytes(request)
        (destination / "request.json").write_bytes(raw)
        state.setdefault("releases", {})[rid] = {"version": state["head"], "status": "prepared", "request_sha256": digest(raw)}
        save_state(root, state, {"action": "prepare-release", "release": rid})
        return {"release": rid, "status": "awaiting_lawyer_confirmation", "project_name": display,
                "output_dir_name": dirname, "name_normalized": display != dirname,
                "candidates": [{"source": str(root / "versions" / state["head"] / "files" / f["source"]),
                                "destination": str(folder / f["output_name"])} for f in outputs]}


def check_request_current(root, state, request):
    manifest, reviews_hash = release_readiness(root, state)
    if (state["head"] != request["version"] or reviews_hash != request["reviews_sha256"]
            or state["versions"][state["head"]]["manifest_sha256"] != request["manifest_sha256"]):
        raise WorkflowError("Version or effective review changed after preparation; prepare and confirm the current release again.")
    for item in request["files"]:
        if manifest["files"].get(item["source"]) != item["sha256"]:
            raise WorkflowError("Confirmed delivery candidate changed.")


def confirm_release(root, release_id, confirmation):
    identifier(release_id)
    for field in ("text", "source_ref"):
        if not isinstance(confirmation.get(field), str) or not confirmation[field].strip():
            raise WorkflowError("Confirmation requires the actual lawyer text and message/source reference.")
    if confirmation.get("decision") != "approve":
        raise WorkflowError("Record explicit lawyer approval of the proposed files, names and scope.")
    with locked(root):
        state = state_at(root)
        record = state.get("releases", {}).get(release_id)
        if not record or record["status"] == "revoked":
            raise WorkflowError("Unknown or revoked release request.")
        request = release_record(root, release_id, record)
        check_request_current(root, state, request)
        if record.get("confirmation_sha256"):
            return {"release": release_id, "status": record["status"], "already_confirmed": True}
        path = inside(root, f"releases/{release_id}/confirmation.json")
        data = {"text": confirmation["text"], "source_ref": confirmation["source_ref"], "decision": "approve",
                "recorded_at": now(), "request_sha256": record["request_sha256"],
                "identity_boundary": "Actual user message must be checked by the host; this record is not authentication."}
        if path.exists():
            prior = read_json(path)
            if any(prior.get(k) != data[k] for k in ("text", "source_ref", "decision", "request_sha256")):
                raise WorkflowError("An unregistered confirmation exists; inspect it instead of replacing it.")
        else:
            with path.open("xb") as stream:
                stream.write(json_bytes(data))
                stream.flush()
                os.fsync(stream.fileno())
        record.update(status="confirmed", confirmation_sha256=digest(path.read_bytes()))
        state["project_name_display"] = request["project_name_display"]
        state["output_dir_name"] = request["output_dir_name"]
        save_state(root, state, {"action": "confirm-release", "release": release_id, "source_ref": confirmation["source_ref"]})
        return {"release": release_id, "status": "confirmed", "published": False}


def publish_release(root, release_id):
    identifier(release_id)
    with locked(root):
        state = state_at(root)
        record = state.get("releases", {}).get(release_id)
        if not record or record["status"] == "revoked" or not record.get("confirmation_sha256"):
            raise WorkflowError("Formal publication requires a recorded, non-revoked lawyer confirmation.")
        request = release_record(root, release_id, record)
        workspace = Path(request["workspace"])
        no_links(workspace)
        with locked(workspace):
            registry_path, owners = output_registry(workspace)
            folder = output_target(root, workspace, request, owners, release_id)
            outputs = [str(folder / item["output_name"]) for item in request["files"]]
            if record["status"] == "published":
                if not all(Path(path).is_file() for path in outputs):
                    raise WorkflowError("A published file is missing; inspect history rather than silently recreating it.")
                return {"release": release_id, "status": "published", "files": outputs, "already_published": True}
            check_request_current(root, state, request)
            attempt_dir = inside(root, f"releases/{release_id}/attempts/{uuid.uuid4().hex}")
            attempt_dir.mkdir(parents=True)
            attempt = {"started_at": now(), "status": "publishing", "files": outputs}
            atomic_write(attempt_dir / "attempt.json", json_bytes(attempt))
            try:
                # Reserve names before writing files so interrupted publication is attributable.
                owner = owners.setdefault(request["output_dir_name"].casefold(), {
                    "matter": root.relative_to(workspace).as_posix(), "matter_id": state["matter_id"], "files": {}})
                for item in request["files"]:
                    owner["files"][item["output_name"].casefold()] = {"release_id": release_id, "sha256": item["sha256"]}
                registry_path.parent.mkdir(exist_ok=True)
                atomic_write(registry_path, json_bytes(owners))
                folder.mkdir(parents=True, exist_ok=True)
                no_links(folder)
                for index, item in enumerate(request["files"]):
                    destination = inside(workspace, "output/" + request["output_dir_name"] + "/" + item["output_name"])
                    if destination.exists():
                        if digest(destination.read_bytes()) != item["sha256"]:
                            raise WorkflowError("A reserved output has unexpected contents; preserve it for inspection.")
                        continue
                    source = inside(root, f"versions/{request['version']}/files/{item['source']}")
                    staging = attempt_dir / f"candidate-{index}"
                    with source.open("rb") as original, staging.open("xb") as stream:
                        shutil.copyfileobj(original, stream)
                        stream.flush()
                        os.fsync(stream.fileno())
                    if digest(staging.read_bytes()) != item["sha256"]:
                        raise WorkflowError("Candidate changed during publication; no replacement is permitted.")
                    # Both directories are in one unlinked workspace. Hard-link publication
                    # is atomic and fails if the target exists on Windows AND POSIX.
                    os.link(staging, destination)
                    staging.unlink()
                output_target(root, workspace, request, owners, release_id)
                attempt.update(status="files_written", files_written_at=now())
                atomic_write(attempt_dir / "attempt.json", json_bytes(attempt))
                record.update(status="published", published_at=now(), output_files=outputs)
                state["last_published_release"] = release_id
                state["last_published_version"] = request["version"]
                try:
                    save_state(root, state, {"action": "publish-release", "release": release_id, "files": outputs})
                except OSError:
                    committed = state_at(root)
                    if committed.get("releases", {}).get(release_id, {}).get("status") != "published":
                        raise
                    return {"release": release_id, "status": "published", "files": outputs,
                            "index_warning": "Publication committed; WORK index needs rebuilding with status."}
                return {"release": release_id, "status": "published", "files": outputs}
            except (OSError, WorkflowError) as error:
                any_written = any(Path(p).exists() for p in outputs)
                status_value = "pending_registration" if any_written else "failed"
                attempt.update(status=status_value, error=str(error), failed_at=now())
                try:
                    atomic_write(attempt_dir / "attempt.json", json_bytes(attempt))
                    # Read the authoritative state again: never undo a successful commit.
                    current = state_at(root)
                    if current.get("releases", {}).get(release_id, {}).get("status") != "published":
                        current["releases"][release_id].update(status=status_value, last_error=str(error))
                        save_state(root, current, {"action": "publication-failed", "release": release_id})
                except OSError:
                    pass
                return {"release": release_id, "status": status_value, "error": str(error),
                        "files_written": [p for p in outputs if Path(p).exists()], "confirmed": True,
                        "next_step": "Inspect the recorded attempt and retry this release; do not rewrite the candidate."}


def revoke_release(root, release_id, reason):
    if not reason.strip():
        raise WorkflowError("Revoking a release requires the actual reason.")
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        record = state.get("releases", {}).get(release_id)
        if not record or record["status"] == "published":
            raise WorkflowError("Only an unpublished release can be revoked; published history remains intact.")
        record.update(status="revoked", revoked_at=now(), revocation_reason=reason)
        save_state(root, state, {"action": "revoke-release", "release": release_id, "reason": reason})
    return {"release": release_id, "status": "revoked"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Absolute matter directory shared by both conversations")
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("--matter-id", required=True)
    copy = commands.add_parser("checkout")
    copy.add_argument("--actor", required=True, help="Actual conversation identifier, recorded rather than authenticated")
    copy.add_argument("--from-version", help="Copy old content into a NEW submission based on current head")
    submission = commands.add_parser("submit")
    submission.add_argument("--draft", required=True)
    submission.add_argument("--verification", help="Legacy pair path inside draft/files")
    submission.add_argument("--clean", help="Legacy pair path inside draft/files")
    submission.add_argument("--deliverables", help="Managed package JSON path inside draft/files")
    submission.add_argument("--execution-ref", help="Actual generation conversation/message record")
    start = commands.add_parser("start-review")
    start.add_argument("--actor", required=True)
    start.add_argument("--version")
    end = commands.add_parser("finish-review")
    end.add_argument("--review", required=True)
    cancel = commands.add_parser("cancel-review")
    cancel.add_argument("--review", required=True)
    cancel.add_argument("--reason", required=True)
    commands.add_parser("status")
    commands.add_parser("discover", help="Read only metadata in this root and its direct matters children")
    binding = commands.add_parser("bind", help="Use --root WORKSPACE; bind each manually started conversation")
    binding.add_argument("--actor", required=True)
    binding.add_argument("--role", choices=("generation", "review"), required=True)
    binding.add_argument("--matter")
    binding.add_argument("--create", action="store_true", help="Create only when no registered candidate exists")
    binding.add_argument("--new", action="store_true", help="Explicit new business matter")
    binding.add_argument("--project-name")
    prepare = commands.add_parser("prepare-release")
    prepare.add_argument("--workspace", required=True, type=Path)
    prepare.add_argument("--project-name")
    prepare.add_argument("--file-name")
    prepare.add_argument("--deliverable", action="append")
    confirm = commands.add_parser("confirm-release")
    confirm.add_argument("--release", required=True)
    confirm.add_argument("--confirmation-file", required=True, help="JSON inside the matter: decision, text, source_ref")
    publish = commands.add_parser("publish")
    publish.add_argument("--release", required=True, help="Retry uses the SAME release identifier")
    revoke = commands.add_parser("revoke-release")
    revoke.add_argument("--release", required=True)
    revoke.add_argument("--reason", required=True)
    pair = commands.add_parser("check-pair", help="Read only Markdown footnote and optional common-body checks; no legal verdict")
    pair.add_argument("--verification", required=True)
    pair.add_argument("--clean", required=True)
    pair.add_argument("--common-start")
    pair.add_argument("--common-end")
    args = parser.parse_args()
    try:
        no_links(args.root)
        root = args.root.resolve()
        if args.command == "init":
            result = init_project(root, args.matter_id)
        elif args.command == "checkout":
            result = checkout(root, args.actor, args.from_version)
        elif args.command == "submit":
            result = submit(root, args.draft, args.verification, args.clean, args.deliverables, args.execution_ref)
        elif args.command == "start-review":
            result = start_review(root, args.actor, args.version)
        elif args.command == "finish-review":
            result = finish_review(root, args.review)
        elif args.command == "cancel-review":
            result = cancel_review(root, args.review, args.reason)
        elif args.command == "discover":
            result = discover(root)
        elif args.command == "bind":
            result = bind_matter(root, args.actor, args.role, args.matter, args.create, args.new, args.project_name)
        elif args.command == "prepare-release":
            no_links(args.workspace)
            result = prepare_release(root, args.workspace.resolve(), args.project_name, args.file_name, args.deliverable)
        elif args.command == "confirm-release":
            result = confirm_release(root, args.release, read_json(inside(root, args.confirmation_file)))
        elif args.command == "publish":
            result = publish_release(root, args.release)
        elif args.command == "revoke-release":
            result = revoke_release(root, args.release, args.reason)
        elif args.command == "check-pair":
            result = check_pair(root, args.verification, args.clean, args.common_start, args.common_end)
        else:
            result = status(root)
    except (WorkflowError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("status") in ("failed", "pending_registration") else 0


if __name__ == "__main__":
    # Keep machine-readable output stable for Chinese paths on Windows hosts.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())

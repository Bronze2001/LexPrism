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
import sys
import uuid


TEMPLATES = Path(__file__).resolve().parents[1] / "templates" / "legal-project"
CHECKS = ("evidence", "coverage", "prose", "views")
TEXT_SUFFIXES = {".md", ".txt", ".json", ".csv"}


class WorkflowError(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


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


def identifier(value):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,100}", value):
        raise WorkflowError("Identifiers must contain letters, digits, underscores or hyphens.")
    return value


def inside(root, relative):
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise WorkflowError(f"Expected a relative path without parent traversal: {relative}")
    candidate = root / relative
    if not candidate.resolve().is_relative_to(root.resolve()):
        raise WorkflowError(f"Path leaves project directory: {relative}")
    return candidate


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
    state = read_json(root / "state.json")
    if state.get("schema_version") != 1:
        raise WorkflowError("Unsupported project state schema.")
    return state


def checked_version(root, state, version):
    if version not in state["versions"]:
        raise WorkflowError(f"Unknown version: {version}")
    folder = root / "versions" / version
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
    if record["status"] == "complete":
        if inventory(root / "reviews" / review_id / "final") != record["files"]:
            raise WorkflowError(f"Completed review changed: {review_id}")


def verify_history(root, state):
    for version in state["versions"]:
        checked_version(root, state, version)
    for review_id, record in state["reviews"].items():
        checked_review(root, review_id, record)


def effective_reviews(state):
    records = [(key, value) for key, value in state["reviews"].items()
               if value["version"] == state["head"]]
    superseded = {key for _, record in records if record["status"] == "complete"
                  for key in record.get("supersedes", [])}
    return [(key, value) for key, value in records if key not in superseded]


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
    lines += ["", "文件共享不会自动唤醒下一对话；律师只需启动对应职责，Agent 自行读取项目记录。", ""]
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
    if root.exists() and any(root.iterdir()):
        raise WorkflowError("Initialize in a new or empty matter directory; existing files are never overwritten.")
    if not (TEMPLATES / "PROJECT.md").is_file():
        raise WorkflowError("Project templates unavailable. Use the original project kit to initialize.")
    root.mkdir(parents=True, exist_ok=True)
    for name in ("inputs", "drafts", "versions", "reviews"):
        (root / name).mkdir()
    for name in ("AGENTS.md", "PROJECT.md"):
        shutil.copyfile(TEMPLATES / name, root / name)
    shutil.copyfile(Path(__file__), root / "document_workflow.py")
    state = {"schema_version": 1, "matter_id": matter_id, "revision": 0,
             "head": None, "versions": {}, "reviews": {}, "events": []}
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


def submit(root, draft_id, verification, clean):
    identifier(draft_id)
    verification, clean = Path(verification).as_posix(), Path(clean).as_posix()
    if verification == clean:
        raise WorkflowError("Two distinct view files are required.")
    with locked(root):
        state = state_at(root)
        verify_history(root, state)
        draft = root / "drafts" / draft_id
        metadata = read_json(draft / "draft.json")
        if metadata["base"] != state["head"]:
            raise WorkflowError("Submission base is stale. Read the new version and integrate in a fresh draft.")
        files = draft / "files"
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
        manifest_data = json_bytes(manifest)
        (staging / "manifest.json").write_bytes(manifest_data)
        staging.rename(root / "versions" / version)
        state["versions"][version] = {k: manifest[k] for k in ("parent", "actor", "pair", "created_at")}
        state["versions"][version]["manifest_sha256"] = digest(manifest_data)
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
        result = {"version": version, "summary": "", "execution_ref": "",
                  "checks": {key: {"status": "PENDING", "evidence": ""} for key in CHECKS},
                  "findings": [], "unperformed_checks": [], "supersedes": [], "supersedes_reason": ""}
        (folder / "result.json").write_bytes(json_bytes(result))
        (folder / "REVIEW.md").write_text("", encoding="utf-8")
        state["reviews"][rid] = {"version": version, "actor": actor, "status": "open", "started_at": now(),
                                  "manifest_sha256": state["versions"][version]["manifest_sha256"]}
        save_state(root, state, {"action": "start-review", "review": rid, "version": version})
    return {"review": rid, "directory": str(folder), "version": version}


def validate_result(root, state, record, result):
    version = record["version"]
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
        anchor = finding.get("anchor", {})
        if anchor.get("version") != version or anchor.get("file") not in manifest["pair"].values():
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
    if "PENDING" in statuses or gaps:
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
        staging.rename(folder / "final")
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
    return {"head": state["head"], "status": current_status(state), "revision": state["revision"]}


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
    submission.add_argument("--verification", required=True, help="Relative file path inside draft/files")
    submission.add_argument("--clean", required=True, help="Relative file path inside draft/files")
    start = commands.add_parser("start-review")
    start.add_argument("--actor", required=True)
    start.add_argument("--version")
    end = commands.add_parser("finish-review")
    end.add_argument("--review", required=True)
    cancel = commands.add_parser("cancel-review")
    cancel.add_argument("--review", required=True)
    cancel.add_argument("--reason", required=True)
    commands.add_parser("status")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.command == "init":
            result = init_project(root, args.matter_id)
        elif args.command == "checkout":
            result = checkout(root, args.actor, args.from_version)
        elif args.command == "submit":
            result = submit(root, args.draft, args.verification, args.clean)
        elif args.command == "start-review":
            result = start_review(root, args.actor, args.version)
        elif args.command == "finish-review":
            result = finish_review(root, args.review)
        elif args.command == "cancel-review":
            result = cancel_review(root, args.review, args.reason)
        else:
            result = status(root)
    except (WorkflowError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

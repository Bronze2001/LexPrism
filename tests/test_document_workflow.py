"""Behavioral checks for document history, review binding and concurrent edits."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import shutil
import uuid
import unittest
from unittest.mock import patch


REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("document_workflow", REPO / "scripts/document_workflow.py")
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        test_base = (REPO / "private" / "workflow-tests").resolve()
        test_base.mkdir(parents=True, exist_ok=True)
        # Normal inherited Windows ACLs; Python 3.14 tempfile's private ACL is
        # incompatible with this desktop sandbox's restricted process identity.
        target = (test_base / uuid.uuid4().hex).resolve()
        target.mkdir()
        assert target.is_relative_to(test_base)
        def cleanup():
            resolved = target.resolve()
            assert resolved.is_relative_to(test_base) and resolved != test_base
            shutil.rmtree(resolved)
        self.addCleanup(cleanup)
        self.root = target / "matter"
        w.init_project(self.root, "synthetic-test")

    def draft(self, actor="generation-a", body="第一段：待验证的示例事实。", source=None):
        draft = w.checkout(self.root, actor, source)
        files = Path(draft["files"])
        for name, text in {"verification.md": body + "\n核验记录：仅合成测试。",
                           "clean.md": body, "BRIEF.md": "合成流程测试，不构成法律意见。",
                           "RESPONSE.md": "本轮修改说明：合成流程测试。"}.items():
            (files / name).write_text(text, encoding="utf-8")
        return draft

    def submit(self, draft=None):
        return w.submit(self.root, (draft or self.draft())["draft"], "verification.md", "clean.md")["version"]

    def review(self, version=None, actor="review-b"):
        return w.start_review(self.root, actor, version)["review"]

    def result(self, rid, change=None):
        folder = self.root / "reviews" / rid
        result = w.read_json(folder / "result.json")
        result.update(summary="合成流程测试的审阅记录。", execution_ref="synthetic-test-record; not a real legal review")
        result.update(findings=[], unperformed_checks=[], supersedes=[], supersedes_reason="")
        result["checks"] = {key: {"status": "PASS", "evidence": "仅对合成材料验证登记逻辑。"} for key in w.CHECKS}
        if change:
            change(result)
        for finding in result["findings"]:
            finding.setdefault("kind", "error" if finding["blocking"] else "preference")
            finding.setdefault("basis", "合成材料与明确测试要求，仅检验程序行为。")
            if finding["status"] == "RESOLVED":
                finding.setdefault("resolution", "合成复审记录：已核对修订内容。")
        (folder / "result.json").write_bytes(w.json_bytes(result))
        (folder / "REVIEW.md").write_text("# 合成审阅\n本文件仅用于程序测试。", encoding="utf-8")
        return result

    def test_full_submit_review_revision_cycle_preserves_history(self):
        first = self.submit()
        original = (self.root / "versions" / first / "files/clean.md").read_bytes()
        rid = self.review()
        self.result(rid, lambda r: r["checks"]["prose"].update(status="REVISE"))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "REVISE")
        second = self.submit(self.draft(body="第一段：修订后的合成事实。"))
        self.assertEqual(w.status(self.root)["status"], "AWAITING_REVIEW")
        second_review = self.review()
        self.result(second_review)
        self.assertEqual(w.finish_review(self.root, second_review)["current_status"], "PASS")
        self.assertEqual(original, (self.root / "versions" / first / "files/clean.md").read_bytes())
        self.assertIn("修订后的合成事实", (self.root / "versions" / second / "CHANGES.md").read_text(encoding="utf-8"))

    def test_discovery_finds_sibling_matter_without_writing(self):
        workspace = self.root.parent / "workspace"
        matter = workspace / "matters" / "client-a"
        w.init_project(matter, "client-a")
        before = w.inventory(workspace)
        result = w.discover(workspace)
        self.assertEqual(result["matters"][0]["root"], str(matter.resolve()))
        self.assertFalse(result["selection_required"])
        self.assertEqual(before, w.inventory(workspace))
        w.init_project(workspace / "matters" / "client-b", "client-b")
        self.assertTrue(w.discover(workspace)["selection_required"])

    def test_discovery_reports_bad_state_and_does_not_scan_other_folders(self):
        workspace = self.root.parent / "workspace"
        broken = workspace / "matters" / "broken"
        broken.mkdir(parents=True)
        (broken / "state.json").write_text("{}", encoding="utf-8")
        w.init_project(workspace / "unrelated" / "hidden", "hidden")
        result = w.discover(workspace)
        self.assertEqual(result["matters"], [])
        self.assertEqual(len(result["errors"]), 1)
        self.assertTrue(result["selection_required"])

    def test_pair_detects_orphan_undefined_duplicate_and_body_drift(self):
        folder = Path(self.draft()["files"])
        a = "title\n<!-- start -->\n结论[^a]。\n[^a]: 来源\n[^orphan]: 未使用\n<!-- end -->"
        b = a.replace("结论[^a]", "改变后的结论[^missing]") + "\n[^a]: 重复\n"
        (folder / "verification.md").write_text(a, encoding="utf-8")
        (folder / "clean.md").write_text(b, encoding="utf-8")
        before = w.inventory(folder)
        result = w.check_pair(folder, "verification.md", "clean.md", "<!-- start -->", "<!-- end -->")
        notes = result["files"]["clean"]["footnotes"]
        self.assertEqual(notes["undefined"], ["missing"])
        self.assertEqual(notes["unused"], ["a", "orphan"])
        self.assertEqual(notes["duplicates"], ["a"])
        self.assertEqual(result["common_body"], "DIFFERENT")
        self.assertEqual(result["legal_review"], "NOT_PERFORMED")
        self.assertEqual(before, w.inventory(folder))

    def test_pair_does_not_guess_body_and_checks_explicit_boundaries(self):
        folder = Path(self.draft()["files"])
        self.assertEqual(w.check_pair(folder, "verification.md", "clean.md")["common_body"], "NOT_CHECKED")
        with self.assertRaisesRegex(w.WorkflowError, "exactly once"):
            w.check_pair(folder, "verification.md", "clean.md", "MISSING_START", "MISSING_END")
        with self.assertRaises(w.WorkflowError):
            w.check_pair(folder, "verification.md", "../state.json")
        text = "<!-- start -->正文[^1]\n[^1]: 来源\n<!-- end -->"
        for name in ("verification.md", "clean.md"):
            (folder / name).write_text(text, encoding="utf-8")
        self.assertEqual(w.check_pair(folder, "verification.md", "clean.md", "<!-- start -->", "<!-- end -->")["common_body"], "IDENTICAL")

    def test_footnotes_ignore_definitions_code_and_escaped_references(self):
        text = "正文[^1]\n[^1]: 来源\n    续行中的[^not_body]\n\n```md\n[^code]\n```\n`[^inline]` 与 \\[^^escape] 和 \\[^escaped]"
        self.assertEqual(w.markdown_footnotes(text), {"undefined": [], "unused": [], "duplicates": []})

    def test_unverified_core_finding_is_pending_even_if_dimensions_say_pass(self):
        self.submit()
        rid = self.review()
        self.result(rid, lambda r: r["findings"].append({
            "id": "I003", "kind": "unverified", "blocking": True, "status": "OPEN",
            "reason": "现行依据欠缺", "requested_change": "补充依据", "acceptance": "复核材料",
            "anchor": {"version": "v0001", "file": "clean.md", "scope": "document"}}))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "PENDING")

    def test_new_review_cannot_drop_protocol_or_resolve_without_reason(self):
        self.submit()
        rid = self.review()
        result = self.result(rid)
        path = self.root / "reviews" / rid / "result.json"
        result.pop("review_protocol")
        path.write_bytes(w.json_bytes(result))
        with self.assertRaisesRegex(w.WorkflowError, "protocol cannot change"):
            w.finish_review(self.root, rid)
        result["review_protocol"] = 2
        finding = {"id": "I004", "kind": "error", "basis": "具体合成证据", "blocking": True,
                   "status": "RESOLVED", "reason": "测试", "requested_change": "修正", "acceptance": "复核",
                   "anchor": {"version": "v0001", "file": "clean.md", "scope": "document"}}
        result["findings"] = [finding]
        path.write_bytes(w.json_bytes(result))
        with self.assertRaisesRegex(w.WorkflowError, "Resolved findings require"):
            w.finish_review(self.root, rid)
        finding["resolution"] = "复核实际原文后撤回误报，原文确有相应记载。"
        path.write_bytes(w.json_bytes(result))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "PASS")

    def test_correction_requires_basis_and_preference_cannot_block(self):
        self.submit()
        rid = self.review()
        result = self.result(rid, lambda r: r["findings"].append({
            "id": "I005", "blocking": True, "status": "OPEN", "reason": "测试", "requested_change": "修正",
            "acceptance": "复核", "anchor": {"version": "v0001", "file": "clean.md", "scope": "document"}}))
        path = self.root / "reviews" / rid / "result.json"
        result["findings"][0].pop("basis")
        path.write_bytes(w.json_bytes(result))
        with self.assertRaisesRegex(w.WorkflowError, "requires basis"):
            w.finish_review(self.root, rid)
        result["findings"][0].update(basis="措辞偏好", kind="preference")
        path.write_bytes(w.json_bytes(result))
        with self.assertRaisesRegex(w.WorkflowError, "preference cannot block"):
            w.finish_review(self.root, rid)

    def test_legacy_open_review_remains_readable_without_rewriting_history(self):
        self.submit()
        rid = self.review()
        # Model an actual pre-upgrade record, which had no protocol marker.
        state = w.state_at(self.root)
        state["reviews"][rid].pop("review_protocol")
        (self.root / "state.json").write_bytes(w.json_bytes(state))
        result = self.result(rid)
        result.pop("review_protocol")
        (self.root / "reviews" / rid / "result.json").write_bytes(w.json_bytes(result))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "PASS")

    def test_publication_retries_brief_windows_contention(self):
        original_rename = Path.rename
        calls = []
        def interrupted_rename(source, destination):
            calls.append(source)
            if len(calls) == 1:
                error = PermissionError("simulated Windows contention")
                error.winerror = 32
                raise error
            return original_rename(source, destination)
        draft = self.draft()
        with patch.object(Path, "rename", interrupted_rename), patch.object(w.time, "sleep") as sleep:
            self.assertEqual(self.submit(draft), "v0001")
            sleep.assert_called_once_with(0.05)
        self.assertEqual(len(calls), 2)

    def test_permanent_publication_denial_leaves_submission_unregistered(self):
        draft = self.draft()
        error = PermissionError("simulated persistent denial")
        error.winerror = 5
        with patch.object(Path, "rename", side_effect=error) as rename, patch.object(w.time, "sleep"):
            with self.assertRaises(PermissionError):
                self.submit(draft)
        self.assertEqual(rename.call_count, 4)
        self.assertIsNone(w.state_at(self.root)["head"])
        self.assertTrue((Path(draft["files"]) / "clean.md").is_file())
        self.assertFalse((self.root / "versions" / "v0001").exists())

    def test_two_writers_cannot_overwrite_new_head(self):
        a, b = self.draft(), self.draft("generation-b")
        version = self.submit(a)
        with self.assertRaisesRegex(w.WorkflowError, "stale"):
            self.submit(b)
        self.assertEqual(w.status(self.root)["head"], version)

    def test_old_review_cannot_approve_new_version(self):
        first = self.submit()
        rid = self.review(first)
        second = self.submit(self.draft())
        self.result(rid)
        result = w.finish_review(self.root, rid)
        self.assertTrue(result["historical"])
        self.assertEqual(result["current_status"], "AWAITING_REVIEW")
        self.assertEqual(w.status(self.root)["head"], second)

    def test_tampered_submitted_file_blocks_review_finalization(self):
        version = self.submit()
        rid = self.review()
        self.result(rid)
        (self.root / "versions" / version / "files/clean.md").write_text("外部改动", encoding="utf-8")
        with self.assertRaisesRegex(w.WorkflowError, "Submitted files changed"):
            w.finish_review(self.root, rid)
        self.assertEqual(w.state_at(self.root)["reviews"][rid]["status"], "open")

    def test_tampered_completed_review_blocks_status(self):
        self.submit()
        rid = self.review()
        self.result(rid)
        w.finish_review(self.root, rid)
        (self.root / "reviews" / rid / "final/REVIEW.md").write_text("覆盖", encoding="utf-8")
        with self.assertRaisesRegex(w.WorkflowError, "Completed review changed"):
            w.status(self.root)

    def test_missing_view_and_path_escape_rejected(self):
        draft = self.draft()
        with self.assertRaises(w.WorkflowError):
            w.submit(self.root, draft["draft"], "verification.md", "../draft.json")
        (Path(draft["files"]) / "clean.md").unlink()
        with self.assertRaisesRegex(w.WorkflowError, "Missing or empty"):
            self.submit(draft)
        self.assertIsNone(w.status(self.root)["head"])

    def test_same_actor_cannot_self_approve(self):
        self.submit()
        with self.assertRaisesRegex(w.WorkflowError, "generating actor"):
            self.review(actor="generation-a")

    def test_pending_checks_prevent_pass(self):
        self.submit()
        rid = self.review()
        self.result(rid, lambda r: r["unperformed_checks"].append("原始材料尚未取得"))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "PENDING")

    def test_blocking_issue_prevents_pass_and_anchor_must_match(self):
        self.submit()
        rid = self.review()
        finding = {"id": "I001", "blocking": True, "status": "OPEN", "reason": "测试缺陷",
                   "requested_change": "核对事实", "acceptance": "提供材料并修正文稿",
                   "anchor": {"version": "v0001", "file": "clean.md", "section": "第一段",
                              "exact": "不存在的原句", "prefix": "", "suffix": ""}}
        self.result(rid, lambda r: r["findings"].append(deepcopy(finding)))
        with self.assertRaisesRegex(w.WorkflowError, "uniquely located"):
            w.finish_review(self.root, rid)
        finding["anchor"]["exact"] = "待验证的示例事实"
        self.result(rid, lambda r: r["findings"].append(deepcopy(finding)))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "REVISE")

    def test_nonblocking_preference_can_pass(self):
        self.submit()
        rid = self.review()
        self.result(rid, lambda r: r["findings"].append({
            "id": "I002", "blocking": False, "status": "OPEN", "reason": "可选措辞偏好",
            "requested_change": "可选择调整", "acceptance": "不影响当前交付",
            "anchor": {"version": "v0001", "file": "clean.md", "scope": "document"}}))
        self.assertEqual(w.finish_review(self.root, rid)["verdict"], "PASS")

    def test_open_review_prevents_overall_pass_and_can_be_cancelled(self):
        self.submit()
        first, second = self.review(), self.review(actor="review-c")
        self.result(first)
        self.assertEqual(w.finish_review(self.root, first)["current_status"], "IN_REVIEW")
        w.cancel_review(self.root, second, "确认该审阅对话已停止，仅用于流程测试。")
        self.assertEqual(w.status(self.root)["status"], "PASS")

    def test_restore_old_content_creates_new_version(self):
        first = self.submit()
        self.submit(self.draft(body="新的示例事实。"))
        restored = w.checkout(self.root, "restore-a", first)
        third = self.submit(restored)
        self.assertEqual(third, "v0003")
        self.assertEqual(w.read_json(self.root / "versions" / third / "manifest.json")["content_from"], first)
        self.assertEqual(w.status(self.root)["status"], "AWAITING_REVIEW")

    def test_explicit_review_correction_preserves_prior_record(self):
        self.submit()
        old = self.review()
        self.result(old, lambda r: r["checks"]["evidence"].update(status="PENDING"))
        w.finish_review(self.root, old)
        fresh = self.review(actor="review-c")
        def correction(r):
            r.update(supersedes=[old], supersedes_reason="补充完成同一已冻结来源的核对；未更改文稿。")
        self.result(fresh, correction)
        self.assertEqual(w.finish_review(self.root, fresh)["current_status"], "PASS")
        self.assertTrue((self.root / "reviews" / old / "final/REVIEW.md").exists())

    def test_process_lock_and_atomic_state_failure_preserve_head(self):
        self.submit()
        before = (self.root / "state.json").read_bytes()
        with w.locked(self.root):
            with self.assertRaisesRegex(w.WorkflowError, "Another state operation"):
                w.status(self.root)
        state = w.state_at(self.root)
        with patch.object(w.os, "replace", side_effect=OSError("simulated storage failure")):
            with self.assertRaises(OSError):
                w.save_state(self.root, state, {"action": "synthetic-failure"})
        self.assertEqual((self.root / "state.json").read_bytes(), before)

    def test_work_index_can_be_rebuilt(self):
        self.submit()
        expected = (self.root / "WORK.md").read_bytes()
        (self.root / "WORK.md").write_text("损坏的索引", encoding="utf-8")
        w.status(self.root)
        self.assertEqual((self.root / "WORK.md").read_bytes(), expected)


if __name__ == "__main__":
    unittest.main()

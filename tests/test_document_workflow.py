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

"""Synthetic local lifecycle tests. No lawyer approval, model or legal quality claim."""
from pathlib import Path
import shutil
import unittest
import uuid
from unittest.mock import patch
from zipfile import ZipFile

from tests.test_document_workflow import w, REPO


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.base = (REPO / "private/release-tests" / uuid.uuid4().hex).resolve()
        self.base.mkdir(parents=True)
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()
        self.root = self.workspace / "matters/a"
        w.init_project(self.root, "synthetic-a")
        def cleanup():
            target = self.base.resolve()
            assert target.is_relative_to((REPO / "private/release-tests").resolve())
            shutil.rmtree(target)
        self.addCleanup(cleanup)

    def submit(self, two=False):
        draft = w.checkout(self.root, "generation-a")
        files = Path(draft["files"])
        for name in ("BRIEF.md", "RESPONSE.md", "evidence/source.md"):
            (files / name).parent.mkdir(exist_ok=True)
            (files / name).write_text("合成程序测试，不是法律材料或真实审批。", encoding="utf-8")
        items = []
        for did, title in ([('letter', '律师函'), ('memo', '内部备忘录')] if two else [('letter', '律师函')]):
            (files / (did + '.md')).write_text("仅合成核验稿。", encoding="utf-8")
            with ZipFile(files / (did + '.docx'), 'w') as z:
                z.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
                z.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>合成测试</w:t></w:r></w:p></w:body></w:document>')
            items.append(dict(id=did, title=title, purpose='external' if did=='letter' else 'internal',
                              verification=did+'.md', clean=did+'.docx', page_check_required=True,
                              related=['memo'] if two and did=='letter' else []))
        (files/'deliverables.json').write_bytes(w.json_bytes(dict(primary='letter', deliverables=items)))
        return w.submit(self.root, draft['draft'], deliverables='deliverables.json', execution_ref='synthetic-generation-conversation')['version']

    def review(self, change=None):
        rid = w.start_review(self.root, 'review-b')['review']
        folder = self.root/'reviews'/rid
        r = w.read_json(folder/'result.json')
        r.update(summary='合成结果，仅测试程序门槛。', execution_ref='synthetic-independent-review', scope='full')
        manifest = w.checked_version(self.root, w.state_at(self.root), r['version'])
        r['reviewed_deliverables'] = [d['id'] for d in manifest['deliverables']]
        r['independence'] = dict(status='separate_conversation', generation_ref=manifest['generation_execution_ref'], review_ref=r['execution_ref'])
        r['pages'] = dict(status='PASS', evidence='Synthetic assertion exercising record validation, not actual page acceptance.')
        r['checks'] = {c:dict(status='PASS', evidence='Synthetic check only.') for c in w.CHECKS}
        if change: change(r)
        (folder/'result.json').write_bytes(w.json_bytes(r))
        (folder/'REVIEW.md').write_text('合成审阅全文，仅用于程序测试。', encoding='utf-8')
        return rid, w.finish_review(self.root, rid)

    def prepare(self, **kwargs):
        return w.prepare_release(self.root, self.workspace, project_name=kwargs.pop('project_name', '合成项目'), **kwargs)['release']

    def confirm(self, rid):
        return w.confirm_release(self.root, rid, dict(decision='approve', text='合成确认：按提案名称和范围交付本版。', source_ref='synthetic-user-message'))

    def ready(self, two=False):
        self.submit(two); self.review(); rid=self.prepare(); self.confirm(rid); return rid

    def test_managed_release_copies_reviewed_bytes_and_is_idempotent(self):
        rid=self.ready(two=True)
        result=w.publish_release(self.root,rid)
        self.assertEqual(result['status'],'published')
        self.assertEqual(len(result['files']),1)
        p=Path(result['files'][0])
        self.assertEqual(p.name,'律师函_v0001.docx')
        self.assertEqual(p.read_bytes(),(self.root/'versions/v0001/files/letter.docx').read_bytes())
        self.assertEqual(w.publish_release(self.root,rid)['files'],result['files'])
        self.assertEqual(len(list(p.parent.iterdir())),1)

    def test_unreviewed_revise_pending_and_open_review_block_publication(self):
        self.submit()
        with self.assertRaises(w.WorkflowError):self.prepare()
        for status in ('REVISE','PENDING'):
            self.review(lambda r:r['checks']['evidence'].update(status=status))
            with self.assertRaises(w.WorkflowError):self.prepare()
            self.submit()
        self.review()
        rid=self.prepare();self.confirm(rid)
        w.start_review(self.root,'review-c')
        with self.assertRaises(w.WorkflowError):w.publish_release(self.root,rid)
        self.assertFalse((self.workspace/'output').exists())

    def test_confirmation_names_and_scope_are_required(self):
        self.submit();self.review()
        with self.assertRaises(w.WorkflowError):w.prepare_release(self.root,self.workspace)
        rid=self.prepare()
        with self.assertRaises(w.WorkflowError):w.publish_release(self.root,rid)
        with self.assertRaises(w.WorkflowError):w.confirm_release(self.root,rid,dict(text='read it',source_ref='synthetic'))
        self.confirm(rid)
        self.assertEqual(w.state_at(self.root)['project_name_display'],'合成项目')

    def test_limited_review_and_unverified_identity_cannot_release(self):
        for change in (lambda r:r.update(scope='limited'), lambda r:r['independence'].update(status='unverified')):
            self.submit();self.review(change)
            with self.assertRaises(w.WorkflowError):self.prepare()

    def test_required_pages_cannot_be_waived_in_release(self):
        self.submit(); self.review(lambda r:r['pages'].update(status='NOT_REQUIRED'))
        with self.assertRaises(w.WorkflowError):self.prepare()

    def test_new_version_requires_new_review_and_confirmation_and_keeps_old_output(self):
        rid=self.ready(); first=w.publish_release(self.root,rid)['files'][0]
        original=Path(first).read_bytes();self.submit()
        with self.assertRaises(w.WorkflowError):self.prepare()
        self.review();second=self.prepare()
        with self.assertRaises(w.WorkflowError):w.publish_release(self.root,second)
        self.confirm(second);result=w.publish_release(self.root,second)
        self.assertIn('v0002',result['files'][0]);self.assertEqual(Path(first).read_bytes(),original)
        self.assertEqual(w.publish_release(self.root,rid)['files'],[first])

    def test_confirmation_becomes_stale_before_publication(self):
        rid=self.ready();self.submit();self.review()
        with self.assertRaisesRegex(w.WorkflowError,'changed after preparation'):w.publish_release(self.root,rid)

    def test_other_matters_and_unknown_directories_are_not_overwritten(self):
        rid=self.ready();first=w.publish_release(self.root,rid)['files'][0]
        self.root=self.workspace/'matters/b';w.init_project(self.root,'synthetic-b')
        self.submit();self.review()
        with self.assertRaisesRegex(w.WorkflowError,'another matter'):self.prepare()
        (self.workspace/'output/未知目录').mkdir()
        with self.assertRaisesRegex(w.WorkflowError,'ownership is unknown'):self.prepare(project_name='未知目录')
        self.assertTrue(Path(first).exists())

    def test_reserved_names_path_traversal_and_extension_changes_rejected(self):
        self.submit();self.review()
        for name in ('','..','../other','A/B','A\\B','CON','nul.txt','COM1','LPT¹','a.','a:b','a\x01b','x'*81):
            with self.subTest(name=name),self.assertRaises(w.WorkflowError):w.safe_name(name)
        with self.assertRaises(w.WorkflowError):self.prepare(file_name='letter.pdf')
        with self.assertRaises(w.WorkflowError):self.prepare(file_name='../letter')

    def test_confirmation_tampering_and_revocation_block_publication(self):
        rid=self.ready();path=self.root/f'releases/{rid}/confirmation.json'
        original=path.read_bytes();path.write_text('{}',encoding='utf-8')
        with self.assertRaises(w.WorkflowError):w.publish_release(self.root,rid)
        path.write_bytes(original);w.revoke_release(self.root,rid,'合成撤回原因')
        with self.assertRaises(w.WorkflowError):w.publish_release(self.root,rid)

    def test_failed_copy_preserves_confirmation_and_can_retry(self):
        rid=self.ready();before=w.inventory(self.root/'versions');confirmation=(self.root/f'releases/{rid}/confirmation.json').read_bytes()
        with patch.object(w.os,'link',side_effect=PermissionError('synthetic write denied')):
            result=w.publish_release(self.root,rid)
        self.assertEqual(result['status'],'failed');self.assertEqual(before,w.inventory(self.root/'versions'))
        self.assertEqual(confirmation,(self.root/f'releases/{rid}/confirmation.json').read_bytes())
        self.assertEqual(w.publish_release(self.root,rid)['status'],'published')

    def test_files_written_before_state_failure_recover_without_duplicate_copy(self):
        rid=self.ready();write=w.atomic_write;failed=[]
        def fail_once(path,data):
            if path==self.root/'state.json' and not failed:
                failed.append(True);raise OSError('synthetic state failure after file publication')
            return write(path,data)
        with patch.object(w,'atomic_write',side_effect=fail_once):result=w.publish_release(self.root,rid)
        self.assertEqual(result['status'],'pending_registration')
        with patch.object(w.os,'link',side_effect=AssertionError('must reuse already written candidate')):
            result=w.publish_release(self.root,rid)
        self.assertEqual(result['status'],'published')

    def test_index_failure_does_not_undo_committed_publication(self):
        rid=self.ready();write=w.atomic_write
        def fail_index(path,data):
            if path==self.root/'WORK.md':raise OSError('synthetic index failure')
            return write(path,data)
        with patch.object(w,'atomic_write',side_effect=fail_index):result=w.publish_release(self.root,rid)
        self.assertEqual(result['status'],'published');self.assertIn('index_warning',result)
        w.status(self.root)

    def test_partial_multiple_file_release_recovers_each_file_once(self):
        self.submit(two=True);self.review();rid=self.prepare(selected=['letter','memo']);self.confirm(rid)
        link=w.os.link;calls=[]
        def fail_second(a,b):
            calls.append(b)
            if len(calls)==2:raise OSError('synthetic second file failure')
            return link(a,b)
        with patch.object(w.os,'link',side_effect=fail_second):first=w.publish_release(self.root,rid)
        self.assertEqual(first['status'],'pending_registration');self.assertEqual(len(first['files_written']),1)
        self.assertEqual(len(w.publish_release(self.root,rid)['files']),2)

    def test_bound_conversations_share_matter_and_keep_separate_bindings(self):
        a=w.bind_matter(self.workspace,'generation-a','generation',matter='matters/a')
        b=w.bind_matter(self.workspace,'review-b','review',matter='matters/a')
        self.assertEqual(a['root'],b['root'])
        other=w.bind_matter(self.workspace,'generation-c','generation',new=True,project_name='第二项目')
        self.assertNotEqual(a['root'],other['root'])
        self.assertEqual(w.bind_matter(self.workspace,'generation-a','generation')['root'],a['root'])
        self.assertFalse(w.bind_matter(self.workspace,'review-c','review')['bound'])
        self.assertTrue(w.bind_matter(self.workspace,'review-c','review',project_name='第二项目')['bound'])

    def test_broken_registered_matter_cannot_be_replaced_by_create(self):
        (self.root/'state.json').write_text('{}',encoding='utf-8')
        with self.assertRaises(w.WorkflowError):w.bind_matter(self.workspace,'generation-a','generation',create=True)
        self.assertEqual(len(list((self.workspace/'matters').iterdir())),1)

    def test_multideliverable_anchors_and_missing_view_validation(self):
        self.submit(two=True)
        def add(r):r['findings'].append(dict(id='I1',kind='preference',basis='synthetic',blocking=False,status='OPEN',reason='synthetic',requested_change='optional',acceptance='optional',anchor=dict(version=r['version'],file='memo.docx',scope='document')))
        self.assertEqual(self.review(add)[1]['verdict'],'PASS')
        d=w.checkout(self.root,'generation-a');p=Path(d['files']);(p/'memo.docx').unlink()
        with self.assertRaises(w.WorkflowError):w.submit(self.root,d['draft'],deliverables='deliverables.json',execution_ref='synthetic')

    def test_malformed_word_and_colliding_titles_are_rejected(self):
        self.submit(two=True);d=w.checkout(self.root,'generation-a');p=Path(d['files']);(p/'letter.docx').write_text('not a Word archive',encoding='utf-8')
        with self.assertRaises(w.WorkflowError):w.submit(self.root,d['draft'],deliverables='deliverables.json',execution_ref='synthetic')
        self.review()
        with self.assertRaises(w.WorkflowError):self.prepare(selected=['letter','letter'])

    def test_old_blocker_cannot_disappear_from_new_full_review(self):
        self.submit()
        def finding(r,status='OPEN'):
            r['findings'].append(dict(id='I-old',kind='error',basis='synthetic evidence',blocking=True,status=status,
                reason='synthetic error',requested_change='repair',acceptance='check new text',
                resolution='synthetic actual new-text check' if status=='RESOLVED' else '',
                anchor=dict(version=r['version'],file='letter.docx',scope='document')))
        self.review(finding);self.submit()
        with self.assertRaisesRegex(w.WorkflowError,'Inherited blocking finding'):self.review()
        for rid,record in w.state_at(self.root)['reviews'].items():
            if record['status']=='open':w.cancel_review(self.root,rid,'synthetic interrupted draft report')
        self.review(lambda r:finding(r,'RESOLVED'))
        self.assertTrue(self.prepare())

    def test_explicit_name_switches_existing_window_binding(self):
        first=w.bind_matter(self.workspace,'generation-a','generation',new=True,project_name='甲项目')
        second=w.bind_matter(self.workspace,'generation-a','generation',new=True,project_name='乙项目')
        self.assertNotEqual(first['root'],second['root'])
        self.assertEqual(w.bind_matter(self.workspace,'generation-a','generation',project_name='甲项目')['root'],first['root'])

    def test_duplicate_release_cannot_reserve_existing_filename(self):
        rid=self.ready();w.publish_release(self.root,rid)
        with self.assertRaises(w.WorkflowError):self.prepare()

    def test_output_lock_prevents_parallel_publication(self):
        rid=self.ready()
        with w.locked(self.workspace),self.assertRaises(w.WorkflowError):w.publish_release(self.root,rid)
        self.assertFalse((self.workspace/'output').exists())

    def test_case_equivalent_unknown_output_is_not_merged(self):
        self.submit();self.review();(self.workspace/'output/Test').mkdir(parents=True)
        with self.assertRaises(w.WorkflowError):self.prepare(project_name='test')


if __name__=='__main__':unittest.main()

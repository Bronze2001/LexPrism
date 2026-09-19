"""Validate the actual shareable ZIP, its template credentials and runnable files."""
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
import uuid
from zipfile import ZipFile

from scripts.build_text_skills import check_archive_links, project_archive_name
from scripts.deployment_check import check, validate_mcp

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'dist'/project_archive_name()


class DeploymentTests(unittest.TestCase):
    def test_mcp_templates_reject_credentials_and_unexpected_fields(self):
        data=json.loads((ROOT/'config/mcp-servers.template.json').read_text(encoding='utf-8'))
        self.assertEqual(validate_mcp(data),15)
        bad=deepcopy(data);bad['mcpServers']['pkulaw-law-search']['headers']['Authorization']='Bearer SYNTHETIC_NON_SECRET_SENTINEL'
        with self.assertRaises(ValueError):validate_mcp(bad)
        bad=deepcopy(data);bad['mcpServers']['pipeworx-legal']['apiKey']='SYNTHETIC_NON_SECRET_SENTINEL'
        with self.assertRaises(ValueError):validate_mcp(bad)

    def test_actual_deployment_zip_has_three_imports_and_only_declared_resources(self):
        with ZipFile(PACKAGE) as z:
            self.assertIsNone(z.testzip());names=z.namelist();prefix='lexprism-project/'
            self.assertFalse(any(x in n.split('/') for n in names for x in ('private','matters','output','runs','.git','.env','.lexprism')))
            manifest=json.loads(z.read(prefix+'deployment-manifest.json'))
            self.assertEqual(set(manifest['files']),{n.removeprefix(prefix) for n in names if n!=prefix+'deployment-manifest.json'})
            for name,sha in manifest['files'].items():self.assertEqual(hashlib.sha256(z.read(prefix+name)).hexdigest(),sha)
            imports=[n for n in names if '/skill-imports/' in n and n.endswith('.zip')]
            self.assertEqual(len(imports),3)
            for name in imports:
                with ZipFile(io.BytesIO(z.read(name))) as skill:
                    self.assertIsNone(skill.testzip());self.assertTrue(any(n.endswith('/SKILL.md') for n in skill.namelist()))
            for name,count in [('mcp-servers.template.json',15),('mcp-pkulaw.template.json',9),('mcp-overseas.template.json',5),('mcp-eurlex.optional.json',1)]:
                self.assertEqual(validate_mcp(json.loads(z.read(prefix+'config/'+name))),count)
            check_archive_links({name:z.read(name) for name in names})
            self.assertNotIn(prefix+'开始部署.md',names)
            self.assertNotEqual(z.read(prefix+'README.md'),z.read(prefix+'docs/律师使用说明.md'))

    def test_extracted_package_passes_offline_check(self):
        base=(ROOT/'private/package-tests'/uuid.uuid4().hex).resolve();base.mkdir(parents=True)
        self.addCleanup(lambda:shutil.rmtree(base) if base.is_relative_to((ROOT/'private/package-tests').resolve()) else None)
        with ZipFile(PACKAGE) as z:
            for name in z.namelist():
                self.assertTrue((base/name).resolve().is_relative_to(base));self.assertNotIn('..',Path(name).parts)
            z.extractall(base)
        self.assertEqual(check(base/'lexprism-project')['offline_package_check'],'PASS')
        workspace=base/'lexprism-project'
        def run(root,*args):
            process=subprocess.run([sys.executable,'-B',str(workspace/'scripts/document_workflow.py'),
                                    '--root',str(root),*args],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(process.returncode,0,process.stderr)
            return json.loads(process.stdout)
        binding=run(workspace,'bind','--actor','synthetic-installed-generator',
                    '--role','generation','--create','--project-name','合成部署验收')
        self.assertTrue(binding['bound']);self.assertTrue(Path(binding['root']).is_dir())
        matter=Path(binding['root'])
        reviewer=run(workspace,'bind','--actor','synthetic-installed-reviewer',
                     '--role','review','--project-name','合成部署验收')
        self.assertEqual(reviewer['root'],binding['root'])
        draft=run(matter,'checkout','--actor','synthetic-installed-generator')
        files=Path(draft['files']);(files/'evidence').mkdir(exist_ok=True)
        for name in ('BRIEF.md','RESPONSE.md','evidence/source.md','核验稿.md'):
            (files/name).write_text('仅合成安装测试，不是法律材料或真实审批。',encoding='utf-8')
        candidate=files/'合成文书.docx'
        with ZipFile(candidate,'w') as z:
            z.writestr('[Content_Types].xml','<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
            z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')
        (files/'deliverables.json').write_text(json.dumps({'primary':'letter','deliverables':[
            dict(id='letter',title='合成文书',purpose='external',verification='核验稿.md',
                 clean=candidate.name,page_check_required=True,related=[])]}),encoding='utf-8')
        submission=run(matter,'submit','--draft',draft['draft'],'--deliverables','deliverables.json',
                       '--execution-ref','synthetic-installed-generation-record')
        self.assertEqual(submission['version'],'v0001')
        review=run(matter,'start-review','--actor','synthetic-installed-reviewer')
        review_dir=matter/'reviews'/review['review']
        result=json.loads((review_dir/'result.json').read_text(encoding='utf-8'))
        result.update(summary='Synthetic package lifecycle check only.',scope='full',
                      execution_ref='synthetic-installed-review-record',reviewed_deliverables=['letter'],
                      independence=dict(status='separate_conversation',
                                        generation_ref='synthetic-installed-generation-record',
                                        review_ref='synthetic-installed-review-record'),
                      pages=dict(status='PASS',evidence='Synthetic record, no real Word page review.'))
        result['checks']={key:dict(status='PASS',evidence='Synthetic program check only.') for key in result['checks']}
        (review_dir/'result.json').write_text(json.dumps(result),encoding='utf-8')
        (review_dir/'REVIEW.md').write_text('Synthetic review, no actual legal conclusion.',encoding='utf-8')
        run(matter,'finish-review','--review',review['review'])
        prepared=run(matter,'prepare-release','--workspace',str(workspace))
        self.assertFalse((workspace/'output').exists())
        (matter/'synthetic-confirmation.json').write_text(json.dumps(dict(decision='approve',
            text='合成确认，不是真实律师批准。',source_ref='synthetic-installed-user-record')),encoding='utf-8')
        run(matter,'confirm-release','--release',prepared['release'],'--confirmation-file','synthetic-confirmation.json')
        published=run(matter,'publish','--release',prepared['release'])
        self.assertEqual(published['status'],'published')
        self.assertEqual(Path(published['files'][0]).read_bytes(),candidate.read_bytes())
        self.assertEqual(run(matter,'publish','--release',prepared['release'])['files'],published['files'])
        (base/'lexprism-project/PROJECT.md').write_text('tampered synthetic file',encoding='utf-8')
        with self.assertRaises(ValueError):check(base/'lexprism-project')


if __name__=='__main__':unittest.main()

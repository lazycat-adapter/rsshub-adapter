from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import upstream

class MetadataTests(unittest.TestCase):
    def test_annotated_tag_is_peeled_by_git_without_api_ref_lookup(self):
        with tempfile.TemporaryDirectory() as directory:
            def git(*args):return subprocess.check_output(['git','-C',directory,*args],text=True).strip()
            git('init','--quiet');git('config','user.email','test@example.com');git('config','user.name','Test')
            git('commit','--quiet','--allow-empty','-m','release');sha=git('rev-parse','HEAD')
            tag='v2026.11.17-9000.'+sha[:7];git('tag','-a',tag,'-m','Release')
            self.assertEqual(upstream.tag_revision(tag,directory),sha)

    def test_published_release_requires_managed_metadata_and_rejects_prerelease(self):
        tag='v2026.11.06-8596.4be79cd'
        with patch.object(upstream,'github_json',return_value={'tag_name':tag,'draft':False,'prerelease':False}):
            self.assertEqual(upstream.published_release(tag)['tag_name'],tag)
        with patch.object(upstream,'github_json',return_value={'tag_name':tag,'draft':False,'prerelease':True}):
            with self.assertRaises(ValueError):upstream.published_release(tag)

    def test_selected_release_rejects_changed_full_revision_with_same_short_prefix(self):
        tag='v2026.11.06-8596.4be79cd';sha='4be79cd'+'a'*33
        with patch.object(upstream,'published_release',return_value={'tag_name':tag}),patch.object(upstream,'tag_revision',return_value='4be79cd'+'b'*33):
            with self.assertRaisesRegex(ValueError,'moved'):
                upstream.validate_selected_release(tag,sha)
